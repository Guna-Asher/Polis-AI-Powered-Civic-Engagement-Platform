from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, init_db
from models import Legislation, Clause, Feedback
from nlp_processor import nlp_processor
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize CORS first, then database
CORS(app)  # This fixes frontend-backend connection issues
init_db(app)

@app.route('/')
def hello():
    return jsonify({"message": "Polis API Server", "version": "1.0"})

@app.route(f'{Config.API_PREFIX}/legislation', methods=['GET'])
def get_legislation():
    status = request.args.get('status', 'active')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = Legislation.query
    if status:
        query = query.filter(Legislation.status == status)
    
    legislation = query.order_by(Legislation.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    result = []
    for leg in legislation.items:
        feedback_stats = db.session.query(
            db.func.avg(Feedback.sentiment_score).label('avg_sentiment'),
            db.func.count(Feedback.id).label('feedback_count')
        ).filter(Feedback.legislation_id == leg.id).first()
        
        result.append({
            'id': leg.id,
            'title': leg.title,
            'description': leg.description,
            'summary': leg.summary,
            'status': leg.status,
            'created_at': leg.created_at.isoformat(),
            'avg_sentiment': float(feedback_stats.avg_sentiment) if feedback_stats.avg_sentiment else 0,
            'feedback_count': feedback_stats.feedback_count or 0
        })
    
    return jsonify({
        'legislation': result,
        'total': legislation.total,
        'pages': legislation.pages,
        'current_page': page
    })

@app.route(f'{Config.API_PREFIX}/legislation/<int:legislation_id>', methods=['GET'])
def get_legislation_detail(legislation_id):
    legislation = Legislation.query.get_or_404(legislation_id)
    clauses = Clause.query.filter_by(legislation_id=legislation_id).all()
    
    clause_data = []
    for clause in clauses:
        clause_feedback = Feedback.query.filter_by(clause_id=clause.id).all()
        sentiment_scores = [fb.sentiment_score for fb in clause_feedback if fb.sentiment_score is not None]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        clause_data.append({
            'id': clause.id,
            'number': clause.clause_number,
            'title': clause.title,
            'content': clause.content,
            'summary': clause.summary,
            'avg_sentiment': avg_sentiment,
            'feedback_count': len(clause_feedback)
        })
    
    return jsonify({
        'legislation': {
            'id': legislation.id,
            'title': legislation.title,
            'description': legislation.description,
            'full_text': legislation.full_text,
            'summary': legislation.summary,
            'status': legislation.status,
            'created_at': legislation.created_at.isoformat()
        },
        'clauses': clause_data
    })

@app.route(f'{Config.API_PREFIX}/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    
    feedback = Feedback(
        legislation_id=data['legislation_id'],
        clause_id=data.get('clause_id'),
        user_id=data.get('user_id', 1),  # Default to user 1 for now
        sentiment_score=data['sentiment_score'],
        tags=data.get('tags', []),
        comment=data.get('comment', ''),
        demographic_data=data.get('demographic_data', {})
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    return jsonify({'message': 'Feedback submitted successfully', 'id': feedback.id}), 201

@app.route(f'{Config.API_PREFIX}/civic-pulse/<int:legislation_id>', methods=['GET'])
def get_civic_pulse(legislation_id):
    sentiment_distribution = db.session.query(
        db.func.count(Feedback.id),
        db.case(
            [(Feedback.sentiment_score > 0.3, 'support'),
             (Feedback.sentiment_score < -0.3, 'oppose')],
            else_='neutral'
        ).label('sentiment_category')
    ).filter(Feedback.legislation_id == legislation_id).group_by('sentiment_category').all()
    
    tag_counts = {}
    all_feedback = Feedback.query.filter_by(legislation_id=legislation_id).all()
    
    for feedback in all_feedback:
        if feedback.tags:
            for tag in feedback.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    demographic_data = {}
    for feedback in all_feedback:
        if feedback.demographic_data:
            for key, value in feedback.demographic_data.items():
                if key not in demographic_data:
                    demographic_data[key] = {}
                demographic_data[key][value] = demographic_data[key].get(value, 0) + 1
    
    return jsonify({
        'sentiment_distribution': [
            {'category': category, 'count': count} 
            for count, category in sentiment_distribution
        ],
        'tag_frequency': tag_counts,
        'demographic_breakdown': demographic_data,
        'total_feedback': len(all_feedback)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
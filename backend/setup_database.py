from app import app, db
from models import Legislation, Clause, User
from nlp_processor import nlp_processor

def setup_database():
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating new tables...")
        db.create_all()
        
        # Create a default user
        default_user = User(
            email="citizen@polis.demo",
            name="Demo Citizen",
            location="Demo City",
            age_group="25-35"
        )
        db.session.add(default_user)
        db.session.commit()
        
        print("Adding sample legislation...")
        
        sample_legislation = [
            {
                'title': 'SB-42: Climate Resilience Act',
                'description': 'Proposes comprehensive climate resilience measures for urban areas',
                'full_text': """
                SECTION 1. SHORT TITLE. This Act may be cited as the "Climate Resilience Act of 2024".

                SECTION 2. FINDINGS. The legislature finds that climate change poses significant risks to urban infrastructure, public health, and economic stability. Recent extreme weather events have demonstrated the urgent need for comprehensive resilience planning.

                SECTION 3. URBAN GREEN INFRASTRUCTURE. All municipalities with populations over 50,000 shall develop and implement green infrastructure plans by January 1, 2026. These plans shall include increased tree canopy coverage and permeable surfaces.

                SECTION 4. FUNDING ALLOCATION. $500 million shall be allocated from the state infrastructure fund to support municipal climate resilience projects.

                SECTION 5. REPORTING REQUIREMENTS. Municipalities shall submit annual progress reports detailing implementation progress and measurable outcomes.
                """,
                'status': 'active'
            },
            {
                'title': 'HB-15: Affordable Housing Act',
                'description': 'Addresses housing affordability through zoning reform and incentives',
                'full_text': """
                ARTICLE 1. PURPOSE. This legislation aims to increase housing affordability and availability through strategic zoning reforms and development incentives.

                ARTICLE 2. ZONING REFORMS. Municipalities shall allow for increased density in transit-oriented development zones. Minimum parking requirements shall be eliminated near public transit stations.

                ARTICLE 3. AFFORDABLE HOUSING SET-ASIDE. Developments with more than 20 units shall set aside 15% of units as affordable housing for households earning less than 80% of area median income.

                ARTICLE 4. TAX INCENTIVES. Property tax abatements shall be available for developers who exceed affordable housing requirements.

                ARTICLE 5. COMMUNITY BENEFITS. Developers receiving incentives shall contribute to community benefit funds.
                """,
                'status': 'active'
            }
        ]
        
        for leg_data in sample_legislation:
            print(f"Adding legislation: {leg_data['title']}")
            
            full_text = leg_data['full_text']
            summary = nlp_processor.summarize_legislation(full_text)
            
            legislation = Legislation(
                title=leg_data['title'],
                description=leg_data['description'],
                full_text=full_text,
                summary=summary,
                status=leg_data['status']
            )
            
            db.session.add(legislation)
            db.session.commit()
            
            if len(full_text) > 200:
                try:
                    clauses = nlp_processor.parse_legislation_structure(full_text)
                    for clause_info in clauses:
                        clause = Clause(
                            legislation_id=legislation.id,
                            clause_number=clause_info['number'],
                            content=clause_info['content'],
                            summary=clause_info['summary']
                        )
                        db.session.add(clause)
                    
                    db.session.commit()
                    print(f"  - Added {len(clauses)} clauses")
                except Exception as e:
                    print(f"  - Error parsing clauses: {e}")
        
        print("Database setup completed successfully!")
        print(f"- Legislation: {Legislation.query.count()}")
        print(f"- Clauses: {Clause.query.count()}")
        print(f"- Users: {User.query.count()}")

if __name__ == '__main__':
    setup_database()
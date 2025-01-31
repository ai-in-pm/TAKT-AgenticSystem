from services.data_service import TaktDataService

def main():
    # Initialize data service
    data_service = TaktDataService()
    
    # Insert sample data for different projects
    projects = ["Project A", "Project B", "Project C"]
    for project in projects:
        print(f"Inserting sample data for {project}...")
        data_service.insert_sample_data(project)
    
    print("Database initialization complete!")

if __name__ == "__main__":
    main()

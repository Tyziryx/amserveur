# collector.py
import os
import sys
import subprocess
import time
from graphiques.graphic import GenerateurGraphiques


def main():
    print("Starting collector...")

    # Get absolute paths
    project_root = os.path.dirname(os.path.abspath(__file__))

    # 1. Generate graphs for the website static folder
    print("Generating graphs...")
    try:
        # Create GenerateurGraphiques with correct DB paths (database is in root directory)
        db_path = os.path.join(project_root, "table_sondes.sqlite")
        cert_db_path = os.path.join(project_root, "parseur", "parseur.sqlite")

        print(f"Using database: {db_path}")

        gen = GenerateurGraphiques(
            db_path=db_path,
            cert_db_path=cert_db_path
        )

        # Ensure output directory exists
        os.makedirs(gen.output_dir, exist_ok=True)

        # Generate all graphs
        gen.generer_tous_graphiques()
        print(f"Graphs generated and saved to {gen.output_dir}")
    except Exception as e:
        print(f"Error generating graphs: {e}")
        import traceback
        traceback.print_exc()

    print("Graph generation completed")


if __name__ == "__main__":
    main()
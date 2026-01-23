#!/usr/bin/env python3
"""
Script to create .env file from template.
Helper script để tạo .env file thuận tiện cho developers.
"""
import os
import sys
from pathlib import Path


def create_env_file(env_path: str = ".env", force: bool = False) -> bool:
    """
    Create .env file from .env.example template.
    
    Args:
        env_path: Path to .env file (default: ".env")
        force: If True, overwrite existing .env file
        
    Returns:
        True if file was created, False otherwise
    """
    # Get base directory (where this script is located)
    base_dir = Path(__file__).parent
    # Try both .env.example and env.example
    example_file = base_dir / ".env.example"
    if not example_file.exists():
        example_file = base_dir / "env.example"
    
    # Check if example file exists
    if not example_file.exists():
        print(f"Error: Example file not found!")
        print(f"Looked for: {base_dir / '.env.example'}")
        print(f"Or: {base_dir / 'env.example'}")
        print("Please ensure env.example exists in base/ directory.")
        return False
    
    # Check if .env already exists
    env_file = Path(env_path)
    if env_file.exists() and not force:
        print(f".env file already exists at {env_file.absolute()}")
        print("Use --force flag to overwrite, or manually edit the existing file.")
        return False
    
    # Read .env.example
    try:
        with open(example_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {example_file}: {e}")
        return False
    
    # Write .env file
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ .env file created successfully at {env_file.absolute()}")
        print("\nNext steps:")
        print("1. Edit .env file and update the following required values:")
        print("   - OPENAI_API_KEY: Your OpenAI API key")
        print("   - MONGODB_URL: Your MongoDB connection string")
        print("   - MONGODB_DB_NAME: Your MongoDB database name")
        print("\n2. Optional: Configure SQL database (PostgreSQL or MySQL)")
        print("\n3. Optional: Add external API keys as needed")
        print("\n4. Run the application:")
        print("   uvicorn app.main:app --reload")
        return True
    except Exception as e:
        print(f"Error writing {env_file}: {e}")
        return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create .env file from .env.example template"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".env",
        help="Output file path (default: .env)"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite existing .env file"
    )
    
    args = parser.parse_args()
    
    success = create_env_file(env_path=args.output, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


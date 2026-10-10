
from pathlib import Path
import tomllib
from supabase import create_client

# Load your saved Supabase credentials
secrets_path = Path(".streamlit") / "secrets.toml"

with secrets_path.open("rb") as file:
    secrets = tomllib.load(file)

url = secrets["SUPABASE_URL"]
key = secrets["SUPABASE_KEY"]

try:
    supabase = create_client(url, key)

    # Query the profiles table without changing any data
    response = (
        supabase.table("profiles")
        .select("user_id")
        .limit(1)
        .execute()
    )

    print("SUCCESS: Connected to Supabase!")
    print("The profiles table is accessible.")
    print("Rows returned:", len(response.data))

except Exception as error:
    print("Connection test failed.")
    print("Error type:", type(error).__name__)
    print("Error details:", str(error))


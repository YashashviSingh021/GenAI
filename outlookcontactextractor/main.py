
import json
import sqlite3
import requests
import msal

# --------------------------------------------------
# 1. Microsoft Entra application configuration
# --------------------------------------------------

TENANT_ID = "6c637512-c417-4e78-9d62-b61258e4b619"
CLIENT_ID = "99eb8ac9-b15a-4737-9a8a-39ce76f99966"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

SCOPES = ["https://graph.microsoft.com/Contacts.Read"]

GRAPH_URL = "https://graph.microsoft.com/v1.0/me/contacts"

# --------------------------------------------------
# 2. Authenticate the user
# --------------------------------------------------

def get_access_token():
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY
    )

    flow = app.initiate_device_flow(scopes=SCOPES)

    if "user_code" not in flow:
        raise RuntimeError(
            f"Could not start authentication: {flow}"
        )

    print(flow["message"])

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(
            f"Authentication failed: "
            f"{result.get('error_description', result.get('error'))}"
        )

    return result["access_token"]


# --------------------------------------------------
# 3. Fetch contacts from Microsoft Graph
# --------------------------------------------------

def fetch_contacts(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "$select": (
            "id,displayName,givenName,surname,"
            "emailAddresses,businessPhones,mobilePhone,"
            "companyName,jobTitle"
        ),
        "$top": "100"
    }

    contacts = []
    next_url = GRAPH_URL

    while next_url:
        response = requests.get(
            next_url,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        contacts.extend(data.get("value", []))

        # Microsoft Graph may return another page.
        next_url = data.get("@odata.nextLink")

        # Parameters are already encoded in nextLink.
        params = None

    return contacts


# --------------------------------------------------
# 4. Create the local SQLite database
# --------------------------------------------------

def create_database():
    with sqlite3.connect("contacts.db") as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                contact_id TEXT PRIMARY KEY,
                display_name TEXT,
                given_name TEXT,
                surname TEXT,
                email_addresses TEXT,
                business_phones TEXT,
                mobile_phone TEXT,
                company_name TEXT,
                job_title TEXT
            )
        """)


# --------------------------------------------------
# 5. Save the extracted contacts
# --------------------------------------------------

def save_contacts(contacts):
    with sqlite3.connect("contacts.db") as connection:
        for contact in contacts:
            emails = json.dumps(
                contact.get("emailAddresses") or []
            )

            business_phones = json.dumps(
                contact.get("businessPhones") or []
            )

            connection.execute("""
                INSERT INTO contacts (
                    contact_id,
                    display_name,
                    given_name,
                    surname,
                    email_addresses,
                    business_phones,
                    mobile_phone,
                    company_name,
                    job_title
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(contact_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    given_name = excluded.given_name,
                    surname = excluded.surname,
                    email_addresses = excluded.email_addresses,
                    business_phones = excluded.business_phones,
                    mobile_phone = excluded.mobile_phone,
                    company_name = excluded.company_name,
                    job_title = excluded.job_title
            """, (
                contact["id"],
                contact.get("displayName"),
                contact.get("givenName"),
                contact.get("surname"),
                emails,
                business_phones,
                contact.get("mobilePhone"),
                contact.get("companyName"),
                contact.get("jobTitle")
            ))


# --------------------------------------------------
# 6. Run the application
# --------------------------------------------------

def main():
    try:
        create_database()

        print("Starting Microsoft authentication...")
        access_token = get_access_token()

        print("Fetching Outlook contacts...")
        contacts = fetch_contacts(access_token)

        print(f"Fetched {len(contacts)} contacts.")

        save_contacts(contacts)

        print("Contacts saved to contacts.db successfully.")

    except requests.HTTPError as error:
        print(f"Microsoft Graph HTTP error: {error}")
        if error.response is not None:
            print(error.response.text)

    except (requests.RequestException, sqlite3.Error, RuntimeError) as error:
        print(f"Application error: {error}")


if __name__ == "__main__":
    main()

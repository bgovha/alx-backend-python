import asyncio
import aiosqlite

async def async_fetch_users():
    """
    Asynchronously fetch all users from the database
    """
    print("Fetching all users...")
    
    # Use async context manager for connection
    async with aiosqlite.connect('users.db') as db:
        # Execute query asynchronously
        async with db.execute("SELECT * FROM users") as cursor:
            # Fetch all results
            results = await cursor.fetchall()
            
            print(f"Fetched {len(results)} users")
            return results

async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40
    """
    print("Fetching users older than 40...")
    
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            results = await cursor.fetchall()
            
            print(f"Fetched {len(results)} users older than 40")
            return results

async def fetch_concurrently():
    """
    Execute both queries concurrently using asyncio.gather
    """
    print("Starting concurrent queries...\n")
    
    # Run both functions at the same time
    # asyncio.gather returns results in the same order as the functions
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("\n" + "="*50)
    print("All Users:")
    for user in all_users:
        print(f"ID: {user[0]}, Name: {user[1]}, Age: {user[2]}")
    
    print("\n" + "="*50)
    print("Users Older Than 40:")
    for user in older_users:
        print(f"ID: {user[0]}, Name: {user[1]}, Age: {user[2]}")
    
    return all_users, older_users


# Run the concurrent fetch
if __name__ == "__main__":
    # asyncio.run() is the entry point for async programs
    asyncio.run(fetch_concurrently())
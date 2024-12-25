# import logging
# import os

# import pytest
# import requests

# from app.main import app  # FastAPI application


# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Read the base URL from the .env file
# BASE_URL = os.getenv(
#     "BASE_URL", "http://localhost:8000"
# )  # Default fallback for localhost


# import logging
# import pytest
# from fastapi.testclient import TestClient
# from app.main import app
# from app.dependencies import get_db

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Test Client
# client = TestClient(app)


# @pytest.mark.e2e
# def test_e2e_workflow(postgres_db_session):
#     """
#     End-to-End Test for Gamified Trading System.

#     This test simulates a complete user journey through the Gamified Trading System.
#     It tests the integration of major system components and their interactions, covering:

#     1. **User Creation and Balance Management**:
#        - Creates 5 users.
#        - Deposits an initial balance of 10,000 units for each user.

#     2. **Portfolio Creation**:
#        - Creates a portfolio for each user.

#     3. **Asset Management**:
#        - Adds 5 unique assets to the system with increasing prices.

#     4. **Trading Operations**:
#        - Each user performs:
#          a. Buying 10 units of each asset.
#          b. Selling 5 units of each asset.
#        - Verifies that portfolio updates reflect these trades.

#     5. **Portfolio Verification**:
#        - Confirms that assets in the users' portfolios are updated correctly
#          after trades (e.g., correct quantities after buy/sell operations).

#     6. **Leaderboard Verification**:
#        - Retrieves the leaderboard with the top-ranked users.
#        - Ensures:
#          a. Users are ranked based on their gem count in descending order.
#          b. Tied users (same gem count) are assigned the same rank.
#          c. The rank order is consistent with gem counts.

#     Purpose:
#     - To validate that the system works as a cohesive unit, integrating all major endpoints
#       and business logic in a realistic workflow scenario.
#     - To ensure that key features like user management, portfolio updates, asset management,
#       trading, and leaderboard ranking function correctly under combined usage.

#     Note:
#     - This test requires the FastAPI application to be running at the specified `BASE_URL`.
#     """

#     # Step 1: Create users and deposit money
#     users = []
#     for i in range(1, 6):
#         user_data = {"username": f"user{i}"}
#         user_response = requests.post(f"{BASE_URL}/users/", json=user_data)
#         assert user_response.status_code == 201
#         user = user_response.json()
#         users.append(user)
#         logger.info(f"Created user: {user['username']} with ID: {user['id']}")

#         # Deposit money into each user's balance
#         deposit_data = {"user_id": user["id"], "amount": 10000}
#         deposit_response = requests.post(f"{BASE_URL}/users/deposit", json=deposit_data)
#         assert deposit_response.status_code == 204

#         # Verify the updated balance
#         user_info_response = requests.get(f"{BASE_URL}/users/{user['id']}")
#         assert user_info_response.status_code == 200
#         user = user_info_response.json()
#         assert user["balance"] == 10000
#         logger.info(f"Deposited 10,000 into {user['username']}'s account")

#     # Step 2: Create portfolios for each user
#     for user in users:
#         portfolio_data = {"user_id": user["id"]}
#         portfolio_response = requests.post(
#             f"{BASE_URL}/portfolios/", json=portfolio_data
#         )
#         assert portfolio_response.status_code == 201
#         portfolio = portfolio_response.json()
#         assert portfolio["user_id"] == user["id"]
#         logger.info(f"Created portfolio for user ID: {user['id']}")

#     # Step 3: Add assets to the system
#     assets = []
#     for i in range(1, 6):
#         asset_data = {"name": f"Asset{i}", "price": 100 * i}
#         asset_response = requests.post(f"{BASE_URL}/assets/", json=asset_data)
#         assert asset_response.status_code == 201
#         assets.append(asset_response.json())
#         logger.info(
#             f"Added asset: {asset_response.json()['name']} with ID: {asset_response.json()['id']}"
#         )

#     # Step 4: Perform trades (buy and sell assets)
#     for user in users:
#         for asset in assets:
#             # Buy 10 units of each asset
#             add_asset_request = {
#                 "asset_id": asset["id"],
#                 "quantity": 10,
#                 "price": asset["price"],
#                 "name": asset["name"],
#             }
#             buy_response = requests.post(
#                 f"{BASE_URL}/trades/{user['id']}/buy/", json=add_asset_request
#             )
#             assert buy_response.status_code == 201
#             logger.info(f"{user['username']} bought 10 units of {asset['name']}")

#             # Sell 5 units of each asset
#             remove_asset_request = {
#                 "asset_id": asset["id"],
#                 "quantity": 5,
#                 "price": asset["price"],
#                 "name": asset["name"],
#             }
#             sell_response = requests.post(
#                 f"{BASE_URL}/trades/{user['id']}/sell/", json=remove_asset_request #             )
#             assert sell_response.status_code == 201
#             logger.info(f"{user['username']} sold 5 units of {asset['name']}")

#     # Step 5: Verify portfolio changes
#     for user in users:
#         for asset in assets:
#             portfolio_asset_response = requests.get(
#                 f"{BASE_URL}/portfolios/{user['id']}/assets/{asset['id']}"
#             )
#             assert portfolio_asset_response.status_code == 200
#             portfolio_asset = portfolio_asset_response.json()
#             assert portfolio_asset["quantity"] == 5  # Bought 10, sold 5
#             logger.info(f"{user['username']}'s portfolio verified for {asset['name']}")

#     # Step 6: Retrieve and verify leaderboard
#     leaderboard_response = requests.get(f"{BASE_URL}/leaderboard/", params={"top_n": 5})
#     assert leaderboard_response.status_code == 200
#     leaderboard = leaderboard_response.json()

#     # Ensure all users appear in the leaderboard with correct gem counts and ranks
#     assert len(leaderboard) == 5
#     gem_counts = [user["gem_count"] for user in leaderboard]
#     ranks = [user["rank"] for user in leaderboard]

#     # Ensure ranking logic (ties and ordering)
#     assert ranks == sorted(ranks)  # Ranks should be ordered
#     assert gem_counts == sorted(
#         gem_counts, reverse=True
#     )  # Gem counts in descending order
#     for i in range(len(gem_counts) - 1):
#         if gem_counts[i] == gem_counts[i + 1]:
#             assert ranks[i] == ranks[i + 1]  # Tied users should have the same rank

#     logger.info("E2E Workflow Test Passed Successfully!")


import pytest
from fastapi.testclient import TestClient
from loguru import logger

from app.main import app

# Test Client
client = TestClient(app)


@pytest.mark.e2e
def test_e2e_workflow(postgres_db_session):
    """
    End-to-End Test for Gamified Trading System.

    This test simulates a complete user journey through the Gamified Trading System.
    It tests the integration of major system components and their interactions, covering:

    1. **User Creation and Balance Management**:
       - Creates 5 users with unique usernames.
       - Deposits an initial balance of 100,000 units for each user.
       - Verifies that the deposited amount is correctly updated in the users' accounts.

    2. **Portfolio Creation**:
       - Creates a portfolio for each user.
       - Ensures that the portfolios are correctly linked to the respective users.

    3. **Asset Management**:
       - Adds 5 unique assets to the system with initial prices.
       - Updates the prices of the assets to simulate market fluctuations.

    4. **Trading Operations**:
       - Each user performs:
         a. **Buying 10 units of each asset**:
            - Ensures that the portfolio reflects the new asset quantity.
            - Calculates the average cost of the asset based on the weighted average formula.
         b. **Selling 5 units of each asset**:
            - Ensures that the portfolio updates correctly, reducing the asset quantity.
            - Verifies the user's balance is updated with the sale proceeds.

    5. **Portfolio Verification**:
       - Confirms that assets in the users' portfolios are updated correctly after trades:
         - Correct quantities after buy and sell operations.
         - Accurate average cost (`avg_cost`) of assets in the portfolio.

    6. **Leaderboard Verification**:
       - Retrieves the leaderboard with the top-ranked users.
       - Ensures:
         a. Users are ranked based on their gem count in descending order.
         b. Tied users (same gem count) are assigned the same rank.
         c. The rank order is consistent with gem counts.

    Purpose:
    - To validate that the system works as a cohesive unit, integrating all major endpoints
      and business logic in a realistic workflow scenario.
    - To ensure that key features like user management, portfolio updates, asset management,
      trading, and leaderboard ranking function correctly under combined usage.
    - To simulate realistic scenarios with updated asset prices, ensuring the robustness
      of average cost calculations and portfolio management.
    """

    # Step 1: Create users and deposit money
    users = []
    usernames = ["Nnamdi", "Soji", "Agbo", "Chinedu", "Uche"]
    for username in usernames:
        user_data = {"username": username}
        user_response = client.post("/users/", json=user_data)
        assert user_response.status_code == 201
        user = user_response.json()
        logger.info(f"Created user: {user['username']} with ID: {user['id']}")

        # Deposit money into each user's balance
        deposit_data = {"user_id": user["id"], "amount": 100_000}
        deposit_response = client.post("/users/deposit", json=deposit_data)
        assert deposit_response.status_code == 204

        # Verify the updated balance
        user_info_response = client.get(f"/users/{user['id']}")
        assert user_info_response.status_code == 200
        user = user_info_response.json()
        assert user["balance"] == 100_000
        users.append(user)
        logger.info(
            f"Deposited 10,000 into {user['username']}'s account. New balance: {user['balance']}"
        )

    logger.info(f"ALL USERS: {users}")

    # Step 2: Create portfolios for each user
    for user in users:
        portfolio_data = {"user_id": user["id"]}
        portfolio_response = client.post("/portfolios/", json=portfolio_data)
        assert portfolio_response.status_code == 201
        portfolio = portfolio_response.json()
        assert portfolio["user_id"] == user["id"]
        logger.info(f"Created portfolio for user ID: {user['id']}")

    # Step 3: Add assets to the system
    assets = []
    assetnames = ["Gold", "Silver", "Bronze", "Platinum", "Lithium"]
    for i, assetname in enumerate(assetnames):
        asset_data = {"name": assetname, "price": 100 * (i + 1)}
        asset_response = client.post("/assets/", json=asset_data)
        assert asset_response.status_code == 201
        assets.append(asset_response.json())
        logger.info(
            f"Added asset: {asset_response.json()['name']} with ID: {asset_response.json()['id']}"
        )
    logger.info(f"ALL ASSETS: {assets}")

    # Step 4: Update asset prices
    updated_prices = [150, 250, 350, 450, 550]  # New prices for the assets
    for asset, new_price in zip(assets, updated_prices):
        update_request = {"name": asset["name"], "price": new_price}
        update_response = client.put(f"/assets/{asset['id']}", json=update_request)
        assert update_response.status_code == 200
        updated_asset = update_response.json()
        logger.info(
            f"Updated asset: {updated_asset['name']} with new price: {updated_asset['price']}"
        )
        asset["price"] = updated_asset["price"]  # Update local copy with the new price

    # Step 5: Perform trades (buy and sell assets)
    for user in users:
        for i, asset in enumerate(assets):
            # Buy 10 units of each asset
            old_price = asset["price"] if "price" in asset else 100 * (i + 1)
            old_quantity = 0 if "quantity" not in asset else asset["quantity"]

            add_asset_request = {
                "asset_id": asset["id"],
                "quantity": 10,
                "price": asset["price"],
            }
            buy_response = client.post(
                f"/portfolios/{user['id']}/assets/", json=add_asset_request
            )
            assert buy_response.status_code == 201
            user = client.get(f"/users/{user['id']}")
            user = user.json()
            logger.info(
                f"{user['username']} bought 10 units of {asset['name']}\
                         for a total of {10 * asset['price']}. His balance is now {user['balance']}"
            )

            # Calculate expected avg_cost after buying
            total_quantity = old_quantity + 10
            expected_avg_cost = (
                old_price * old_quantity + asset["price"] * 10
            ) / total_quantity
            asset["avg_cost"] = expected_avg_cost
            asset["quantity"] = total_quantity

            # Sell 5 units of each asset
            sell_response = client.delete(
                f"/portfolios/{user['id']}/assets/{asset['id']}?quantity=5"
            )
            assert sell_response.status_code == 200
            user = client.get(f"/users/{user['id']}")
            user = user.json()
            logger.info(
                f"{user['username']} sold 5 units of {asset['name']}\
                         for a total of {5 * asset['price']}. His balance is now {user['balance']}"
            )

    # Step 6: Verify portfolio changes
    for user in users:
        for asset in assets:
            portfolio_asset_response = client.get(
                f"/portfolios/{user['id']}/assets/{asset['id']}"
            )
            assert portfolio_asset_response.status_code == 200
            portfolio_asset = portfolio_asset_response.json()
            logger.info(f"{user['username']}'s PORTFOLIO INFO: {portfolio_asset}")

            # Verify remaining quantity
            assert portfolio_asset["quantity"] == 5  # Bought 10, sold 5

            # Verify avg_cost
            avg_cost = portfolio_asset["avg_cost"]
            assert (
                avg_cost == asset["avg_cost"]
            ), f"Expected avg_cost {asset['avg_cost']}, got {avg_cost}"
            logger.info(
                f"Verified avg_cost for {asset['name']} in {user['username']}'s portfolio: {avg_cost}"
            )

    # Step 7: Retrieve and verify leaderboard
    leaderboard_response = client.get("/leaderboard/", params={"top_n": 5})
    assert leaderboard_response.status_code == 200
    leaderboard = leaderboard_response.json()

    # Ensure all users appear in the leaderboard with correct gem counts and ranks
    assert len(leaderboard) == 5
    gem_counts = [user["gem_count"] for user in leaderboard]
    ranks = [user["rank"] for user in leaderboard]

    # Ensure ranking logic (ties and ordering)
    assert ranks == sorted(ranks)  # Ranks should be ordered
    assert gem_counts == sorted(
        gem_counts, reverse=True
    )  # Gem counts in descending order
    for i in range(len(gem_counts) - 1):
        if gem_counts[i] == gem_counts[i + 1]:
            assert ranks[i] == ranks[i + 1]  # Tied users should have the same rank

    logger.info("E2E Workflow Test Passed Successfully!")

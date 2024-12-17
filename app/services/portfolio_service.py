from app.models import Asset, Portfolio, PortfolioAsset
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(self, user_id: int) -> Portfolio:
        """
        Create a new portfolio for a user.
        """
        try:
            existing_portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
            if existing_portfolio:
                raise ValueError("Portfolio already exists.")

            portfolio = Portfolio(user_id=user_id)
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
            return portfolio
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError("Error creating portfolio.") from e

    def get_portfolio(self, user_id: int) -> Portfolio:
        """
        Retrieve a portfolio by user ID.
        """
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            raise ValueError("Portfolio not found.")
        return portfolio


    def add_asset_to_portfolio(self, user_id: int, asset_id: int, quantity: int, price: float) -> PortfolioAsset:
        """
        Add or update an asset in the user's portfolio.
        """
        try:
            # Check if the portfolio exists
            portfolio = self.get_portfolio(user_id)
            
            # Verify the asset exists in the assets table
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                raise ValueError(f"Asset with ID {asset_id} does not exist.")

            # Check if the asset already exists in the portfolio
            portfolio_asset = self.db.query(PortfolioAsset).filter(
                PortfolioAsset.portfolio_id == portfolio.id,
                PortfolioAsset.asset_id == asset_id
            ).first()

            if portfolio_asset:
                portfolio_asset.quantity += quantity
            else:
                portfolio_asset = PortfolioAsset(
                    portfolio_id=portfolio.id, asset_id=asset_id, quantity=quantity, price=price
                )
                self.db.add(portfolio_asset)

            self.db.commit()
            return portfolio_asset
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError("Error adding asset to portfolio.") from e



    def remove_asset(self, user_id: int, asset_id: int, quantity: int) -> None:
        """
        Remove or reduce the quantity of an asset in the user's portfolio.

        If the quantity to remove exceeds the available quantity, raise an error.
        """
        try:
            portfolio = self.get_portfolio(user_id)
            
            # Find the portfolio-asset relationship
            portfolio_asset = self.db.query(PortfolioAsset).filter(
                PortfolioAsset.portfolio_id == portfolio.id,
                PortfolioAsset.asset_id == asset_id
            ).first()

            if not portfolio_asset:
                raise ValueError(f"Asset with ID {asset_id} not found in portfolio.")

            # Check if the quantity to remove exceeds the available quantity
            if quantity > portfolio_asset.quantity:
                raise ValueError(
                    f"Cannot remove {quantity} units of asset {asset_id}. "
                    f"Only {portfolio_asset.quantity} available."
                )

            # Reduce the quantity or delete the asset if quantity becomes zero
            portfolio_asset.quantity -= quantity
            if portfolio_asset.quantity == 0:
                self.db.delete(portfolio_asset)

            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError("Error removing asset from portfolio.") from e


    def list_portfolio_assets(self, user_id: int) -> list[PortfolioAsset]:
        """
        List all assets in a user's portfolio, including quantity and price from PortfolioAsset
        and name from the Asset table.
        """
        try:
            portfolio = self.get_portfolio(user_id)

            # Query PortfolioAsset and join with the Asset table to fetch asset details
            portfolio_assets = (
                self.db.query(PortfolioAsset)
                .join(Asset, PortfolioAsset.asset_id == Asset.id)
                .filter(PortfolioAsset.portfolio_id == portfolio.id)
                .options(joinedload(PortfolioAsset.asset))  # Eager load asset details
                .all()
            )

            if not portfolio_assets:
                raise ValueError(f"No assets found for portfolio with ID {portfolio.id}.")

            return portfolio_assets
        except SQLAlchemyError as e:
            raise ValueError("Error retrieving portfolio assets.") from e
    

    def calculate_portfolio_value(self, user_id: int) -> float:
        """
        Calculate the total value of all assets in the user's portfolio.
        The value of each asset is calculated as quantity * price.
        The price is fetched dynamically from the Asset table.
        """
        try:
            # Retrieve the user's portfolio
            portfolio = self.get_portfolio(user_id)
            
            # Perform a join between PortfolioAsset and Asset to get quantities and current prices
            results = (
                self.db.query(PortfolioAsset.quantity, Asset.price)
                .join(Asset, PortfolioAsset.asset_id == Asset.id)
                .filter(PortfolioAsset.portfolio_id == portfolio.id)
                .all()
            )

            # Calculate the total value by summing quantity * price
            total_value = sum(quantity * price for quantity, price in results)
            return total_value
        
        except ValueError:
            # Handle the case where no portfolios or assets are found
            return 0.0

        except SQLAlchemyError as e:
            raise ValueError("Error calculating portfolio value.") from e


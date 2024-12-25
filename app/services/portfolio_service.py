from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models import Asset, Portfolio, PortfolioAsset, User


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(self, user_id: int) -> Portfolio:
        """
        Create a new portfolio for a user.
        """
        try:
            existing_portfolio = (
                self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
            )
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
        portfolio = (
            self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        )
        if not portfolio:
            raise ValueError("Portfolio not found.")
        return portfolio

    def add_asset_to_portfolio(
        self, user_id: int, asset_id: int, quantity: int
    ) -> PortfolioAsset:
        """
        Buy an asset and add it to the user's portfolio.
        Returns the updated PortfolioAsset with joined Asset details.
        """
        try:
            user = self._get_user(user_id)
            asset = self._get_asset(asset_id)

            total_cost = quantity * asset.price
            if user.balance < total_cost:
                raise ValueError("Insufficient balance to complete the trade.")

            # Deduct the cost from the user's balance
            user.balance -= total_cost

            # Add the asset to the portfolio
            portfolio = self.get_portfolio(user_id)
            portfolio_asset = (
                self.db.query(PortfolioAsset)
                .filter(
                    PortfolioAsset.portfolio_id == portfolio.id,
                    PortfolioAsset.asset_id == asset_id,
                )
                .first()
            )

            if portfolio_asset:
                # Update quantity and calculate weighted average price
                total_quantity = portfolio_asset.quantity + quantity
                portfolio_asset.avg_cost = (
                    portfolio_asset.avg_cost * portfolio_asset.quantity
                    + asset.price * quantity
                ) / total_quantity
                portfolio_asset.quantity = total_quantity
            else:
                # Add the new asset to the portfolio
                portfolio_asset = PortfolioAsset(
                    portfolio_id=portfolio.id,
                    asset_id=asset_id,
                    quantity=quantity,
                    avg_cost=asset.price,
                )
                self.db.add(portfolio_asset)

            # Update trade stats for the user
            self._record_trade(user)
            self.db.commit()

            # Return the updated PortfolioAsset with Asset details
            return self.get_portfolio_asset(user_id, asset_id)

        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError("Error buying asset.") from e

    def remove_asset_from_portfolio(self, user_id: int, asset_id: int, quantity: int):
        """
        Sell an asset and remove it from the user's portfolio.
        """
        try:
            user = self._get_user(user_id)
            portfolio = self.get_portfolio(user_id)

            portfolio_asset = (
                self.db.query(PortfolioAsset)
                .filter(
                    PortfolioAsset.portfolio_id == portfolio.id,
                    PortfolioAsset.asset_id == asset_id,
                )
                .first()
            )

            # Check if the portfolio_asset exists
            if not portfolio_asset:
                raise ValueError(f"Asset with ID {asset_id} not found in portfolio.")

            # if not portfolio_asset:
            #     raise ValueError("Asset not found in portfolio.")
            if portfolio_asset.quantity < quantity:
                raise ValueError("Insufficient quantity to sell.")

            # Calculate proceeds from the sale
            asset = self._get_asset(asset_id)
            proceeds = quantity * asset.price

            # Update quantity or remove the asset if quantity becomes zero
            portfolio_asset.quantity -= quantity
            if portfolio_asset.quantity == 0:
                self.db.delete(portfolio_asset)

            # Add proceeds to the user's balance
            user.balance += proceeds

            # Update trade stats for the user
            self._record_trade(user)
            self.db.commit()
            return portfolio_asset
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError("Error selling asset.") from e

    def get_portfolio_asset(self, user_id: int, asset_id: int) -> PortfolioAsset:
        """
        Retrieve a specific asset in a user's portfolio with asset details.
        """
        portfolio = self.get_portfolio(user_id)

        portfolio_asset = (
            self.db.query(PortfolioAsset)
            .join(Asset, PortfolioAsset.asset_id == Asset.id)  # Join with Asset
            .filter(
                PortfolioAsset.portfolio_id == portfolio.id,
                PortfolioAsset.asset_id == asset_id,
            )
            .options(joinedload(PortfolioAsset.asset))  # Eager load Asset details
            .first()
        )

        if not portfolio_asset:
            raise ValueError(f"Asset with ID {asset_id} not found in portfolio.")

        return portfolio_asset

    def list_portfolio_assets(self, user_id: int) -> list[PortfolioAsset]:
        """
        List all assets in a user's portfolio, including quantity and price.
        """
        try:
            portfolio = self.get_portfolio(user_id)

            portfolio_assets = (
                self.db.query(PortfolioAsset)
                .join(Asset, PortfolioAsset.asset_id == Asset.id)
                .filter(PortfolioAsset.portfolio_id == portfolio.id)
                .options(joinedload(PortfolioAsset.asset))  # Eager load asset details
                .all()
            )
            return portfolio_assets
        except SQLAlchemyError as e:
            raise ValueError("Error retrieving portfolio assets.") from e

    def calculate_portfolio_value(self, user_id: int) -> float:
        """
        Calculate the total value of all assets in the user's portfolio.
        """
        try:
            portfolio = self.get_portfolio(user_id)

            results = (
                self.db.query(PortfolioAsset.quantity, Asset.price)
                .join(Asset, PortfolioAsset.asset_id == Asset.id)
                .filter(PortfolioAsset.portfolio_id == portfolio.id)
                .all()
            )
            return sum(quantity * price for quantity, price in results)
        except SQLAlchemyError as e:
            raise ValueError("Error calculating portfolio value.") from e

    def _record_trade(self, user: User):
        """
        Update trade statistics and gems for the user.
        """
        user.trade_count += 1
        user.gem_count += 1

        # Add bonus gems for milestones
        if user.trade_count == 5:
            user.gem_count += 5
        elif user.trade_count == 10:
            user.gem_count += 10

        self.db.commit()

    def _get_user(self, user_id: int) -> User:
        """
        Retrieve a user by ID.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")
        return user

    def _get_asset(self, asset_id: int) -> Asset:
        """
        Retrieve an asset by ID.
        """
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found.")
        return asset

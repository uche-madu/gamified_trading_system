from sqlalchemy.orm import Session

from app.models import User
from app.services.portfolio_service import PortfolioService
from app.services.user_service import UserService


class TradeService:
    def __init__(
        self,
        db: Session,
        portfolio_service: PortfolioService,
        user_service: UserService,
    ):
        self.db = db
        self.portfolio_service = portfolio_service
        self.user_service = user_service

    def buy_asset(self, user_id: int, asset_id: int, quantity: int, price: float):
        """
        Buy an asset and add it to the user's portfolio.
        """
        # Verify user existence
        user = self.user_service.get_user(user_id)

        # Add or update the asset in the user's portfolio
        self.portfolio_service.add_asset_to_portfolio(
            user_id=user_id, asset_id=asset_id, quantity=quantity, price=price
        )

        # Record the trade and update milestones
        self._record_trade(user)

    def sell_asset(self, user_id: int, asset_id: int, quantity: int):
        """
        Sell an asset from the user's portfolio.
        """
        # Verify user existence
        user = self.user_service.get_user(user_id)

        # Remove or update the asset's quantity in the user's portfolio
        self.portfolio_service.remove_asset(
            user_id=user_id, asset_id=asset_id, quantity=quantity
        )

        # Record the trade and update milestones
        self._record_trade(user)

    def _record_trade(self, user: User):
        """
        Record a trade for a user and update trade count and gem milestones.
        """

        # Increment trade count and base gem count
        user.trade_count += 1
        user.gem_count += 1  # Earn 1 gem per trade

        # Milestone bonuses
        if user.trade_count == 5:
            user.gem_count += 5  # Bonus for 5 trades
        elif user.trade_count == 10:
            user.gem_count += 10  # Bonus for 10 trades

        self.db.commit()

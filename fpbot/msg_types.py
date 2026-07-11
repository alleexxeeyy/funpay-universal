from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from FunPayAPI.account import Account
    from FunPayAPI.types import Message, OrderShortcut, Order, ChatShortcut, Review, UserProfile


@dataclass
class MsgAccount:
    id: int
    username: str
    balance: str
    active_sales: int
    active_purchases: int


def msg_account(acc: "Account") -> MsgAccount:
    if not acc:
        return None
    cur = acc.currency.name if acc.currency else "RUB"
    return MsgAccount(
        id=acc.id or "-",
        username=acc.username or "-",
        balance=f"{acc.total_balance} {cur}",
        active_sales=acc.active_sales or 0,
        active_purchases=acc.active_purchases or 0,
    )


@dataclass
class MsgUser:
    id: str
    username: str


def msg_user_from_message(msg: "Message") -> MsgUser:
    if not msg:
        return None
    return MsgUser(
        id=str(msg.author_id or "-"),
        username=msg.author or "-",
    )


def msg_user_from_profile(profile: "UserProfile") -> MsgUser:
    if not profile:
        return None
    return MsgUser(
        id=str(profile.id or "-"),
        username=profile.username or "-",
    )


@dataclass
class MsgOrder:
    id: str
    title: str
    amount: str
    price: str
    buyer: str
    status: str
    date: str


def msg_order(order: "OrderShortcut") -> MsgOrder:
    if not order:
        return None
    cur = order.currency.name if order.currency else ""
    return MsgOrder(
        id=str(order.id or "-"),
        title=order.description or "-",
        amount=order.amount or "-",
        price=f"{order.price} {cur}" if cur else str(order.price),
        buyer=order.buyer_username or "-",
        status=order.status.name if order.status else "-",
        date=order.date.strftime("%d.%m.%Y %H:%M") if order.date else "-",
    )


@dataclass
class MsgChat:
    id: str
    name: str
    last_message: str


def msg_chat(chat: "ChatShortcut") -> MsgChat:
    if not chat:
        return None
    return MsgChat(
        id=str(chat.id or "-"),
        name=chat.name or "-",
        last_message=chat.last_message_text or "-",
    )


@dataclass
class MsgReview:
    stars: str
    text: str
    author: str
    order_id: str


def msg_review(review: "Review") -> MsgReview:
    if not review:
        return None
    return MsgReview(
        stars="⭐" * (review.stars or 0),
        text=review.text or "-",
        author=review.author or "-",
        order_id=str(review.order_id or "-"),
    )

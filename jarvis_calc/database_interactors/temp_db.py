from jorm.jarvis.db_access import JORMCollector, UserInfoCollector
from jorm.jarvis.db_update import UserInfoChanger, JORMChanger
from jorm.market.infrastructure import Warehouse, Niche
from jorm.market.person import Account, User
from jorm.market.service import Request
from jorm.server.token.types import TokenType

users: dict[int, User] = {}
users_by_login: dict[str, User] = {}
accounts: dict[str, Account] = {}
user_tokens: dict[int, dict[str, dict[TokenType, str]]] = {}


class TempUserInfoCollector(UserInfoCollector):
    def get_user_by_account(self, account: Account) -> User | None:
        if account.email in users_by_login:
            return users_by_login[account.email]
        return None

    def get_user_by_id(self, user_id: int) -> User | None:
        if user_id in users:
            return users[user_id]
        return None

    def get_account(self, login: str) -> Account | None:
        if login in accounts:
            return accounts[login]
        return None

    def get_token_rnd_part(self, user_id: int, imprint: str, token_type: TokenType) -> str:
        return user_tokens[user_id][imprint][token_type]


class TempJORMCollector(JORMCollector):
    def get_niche(self, niche_name: str) -> Niche:
        return Niche("empty niche", {}, 0)

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        pass

    def get_all_warehouses(self) -> list[Warehouse]:
        pass


class TempUserInfoChanger(UserInfoChanger):
    def update_session_tokens(self, old_update_token: str, new_access_token: str, new_update_token: str) -> None:
        for user_id in user_tokens:
            for imprint in user_tokens[user_id]:
                if user_tokens[user_id][imprint][TokenType.UPDATE] == old_update_token:
                    user_tokens[user_id][imprint][TokenType.UPDATE] = new_update_token
                    user_tokens[user_id][imprint][TokenType.ACCESS] = new_access_token
                    return
        raise Exception

    def update_session_tokens_by_imprint(self, access_token: str, update_token: str, imprint_token: str,
                                         user: User) -> None:
        if user.user_id not in user_tokens:
            user_tokens[user.user_id] = {}
        if imprint_token in user_tokens[user.user_id]:
            user_tokens[user.user_id][imprint_token][TokenType.ACCESS] = access_token
            user_tokens[user.user_id][imprint_token][TokenType.UPDATE] = update_token
        else:
            self.save_all_tokens(access_token, update_token, imprint_token, user)

    def save_all_tokens(self, access_token: str, update_token: str, imprint_token: str, user: User) -> None:
        if user.user_id not in user_tokens:
            user_tokens[user.user_id] = {}
        if imprint_token not in user_tokens[user.user_id]:
            user_tokens[user.user_id][imprint_token] = {}
        user_tokens[user.user_id][imprint_token][TokenType.ACCESS] = access_token
        user_tokens[user.user_id][imprint_token][TokenType.UPDATE] = update_token

    def save_user_and_account(self, user: User, account: Account) -> None:
        users[user.user_id] = user
        users_by_login[account.email] = user
        accounts[account.email] = account

    def delete_tokens_for_user(self, user: User, imprint_token: str):
        user_tokens[user.user_id].pop(imprint_token, None)


class TempJORMChanger(JORMChanger):

    def save_request(self, request: Request, user: User) -> None:
        pass

    def load_new_niche(self, niche_name: str) -> Niche:
        pass

from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.facade import (
    PAGINATION_CONTENT_ARGS_REST,
    Auth,
    AuthType,
    HttpFacade,
    MediaType,
    Page,
    PageCursor,
)
from backend.app.core.config import settings


def import_dip_bundestag():
    auth = Auth(auth_type=AuthType.DIPBUNDESTAG_API_TOKEN, token=settings.DIP_BUNDESTAG_API_KEY)
    facade = DIPBundestagFacade(settings.DIP_BUNDESTAG_BASE_URL, auth)

    print(facade.get_drucksachen('2023-11-01T10:00:00'))


if __name__ == '__main__':
    import_dip_bundestag()

"""Tests the app's database interface."""
from appstore.apps import InMemoryAppsDB


def test_in_memory_apps_db() -> None:
    """Test adding an app to InMemoryAppsDB
    and getting its developer and items prices."""
    appsdb = InMemoryAppsDB()
    appsdb.add_app(
        app_id="TrivialDrive",
        developer_id="TrivialDriveDeveloper#2",
        items={"Oil": 1.0, "Antifreeze": 1.20},
    )
    assert appsdb.get_developer_id(app_id="TrivialDrive") == "TrivialDriveDeveloper#2"
    assert appsdb.get_item_price(app_id="TrivialDrive", item="Oil") == 1.0

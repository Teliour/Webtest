import logging
import time
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger()

# --- Page Objects для админ-панели ---

class AdminLoginPage:
    URL = "https://demo.opencart.com/admin/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    @allure.step("Открыть страницу входа в админ-панель")
    def open(self):
        self.driver.get(self.URL)
        logger.info("Открыта страница входа в админ-панель")

    @allure.step("Войти в админ-панель")
    def login(self, username, password):
        self.wait.until(EC.visibility_of_element_located((By.ID, "input-username"))).send_keys(username)
        self.driver.find_element(By.ID, "input-password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        logger.info("Выполнен вход в админ-панель")
        close_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-close")))
        close_btn.click()
        logger.info("Закрыто всплывающее окно")

class AdminCategoryPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    @allure.step("Перейти в раздел Категорий")
    def open(self):
        menu_catalog = self.wait.until(EC.element_to_be_clickable((By.ID, "menu-catalog")))
        menu_catalog.click()
        categories = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Categories")))
        categories.click()
        logger.info("Открыт раздел Категорий")

    @allure.step("Создать новую категорию: {1}")
    def create_category(self, category_name, description="Test description"):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-bs-original-title='Add New']"))).click()
        logger.info("Нажата кнопка создания новой категории")

        self.wait.until(EC.visibility_of_element_located((By.ID, "input-name1"))).send_keys(category_name)
        self.driver.find_element(By.CSS_SELECTOR, "div.note-editable").send_keys(description)
        logger.info(f"Введено имя категории '{category_name}' и описание")

        self.driver.find_element(By.CSS_SELECTOR, "button[data-bs-original-title='Save']").click()
        logger.info(f"Категория '{category_name}' создана")
        time.sleep(2)

class AdminProductPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    @allure.step("Перейти в раздел Товаров")
    def open(self):
        menu_catalog = self.wait.until(EC.element_to_be_clickable((By.ID, "menu-catalog")))
        menu_catalog.click()
        products = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Products")))
        products.click()
        logger.info("Открыт раздел Товаров")

    @allure.step("Добавить товар: {1} в категорию {2}")
    def add_product(self, name, category_name, description="Test product description"):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-bs-original-title='Add New']"))).click()
        logger.info("Нажата кнопка создания нового товара")

        self.wait.until(EC.visibility_of_element_located((By.ID, "input-name1"))).send_keys(name)
        self.driver.find_element(By.ID, "input-meta-title1").send_keys(name)
        self.driver.find_element(By.CSS_SELECTOR, "div.note-editable").send_keys(description)

        self.driver.find_element(By.LINK_TEXT, "Data").click()
        self.wait.until(EC.visibility_of_element_located((By.ID, "input-model"))).send_keys("Model-"+name)

        self.driver.find_element(By.LINK_TEXT, "Links").click()
        category_input = self.wait.until(EC.visibility_of_element_located((By.ID, "input-category")))
        category_input.clear()
        category_input.send_keys(category_name)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".dropdown-menu li a"))).click()

        self.driver.find_element(By.CSS_SELECTOR, "button[data-bs-original-title='Save']").click()
        logger.info(f"Товар '{name}' добавлен в категорию '{category_name}'")
        time.sleep(2)

    @allure.step("Удалить товар: {1}")
    def delete_product_by_name(self, product_name):
        filter_name = self.wait.until(EC.visibility_of_element_located((By.ID, "input-name")))
        filter_name.clear()
        filter_name.send_keys(product_name)
        self.driver.find_element(By.ID, "button-filter").click()
        time.sleep(2)

        checkbox = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox'][name='selected[]']")))
        checkbox.click()
        logger.info(f"Выбран товар для удаления: {product_name}")

        self.driver.find_element(By.CSS_SELECTOR, "button[data-bs-original-title='Delete']").click()
        alert = self.driver.switch_to.alert
        alert.accept()
        logger.info(f"Товар '{product_name}' удалён")
        time.sleep(2)

# --- Тесты ---

@allure.feature("Админ-панель: Управление категориями и товарами")
def test_manage_devices_category_and_products(driver):
    admin_login = AdminLoginPage(driver)
    admin_category = AdminCategoryPage(driver)
    admin_product = AdminProductPage(driver)
    main_page = MainPage(driver)  

    admin_login.open()
    admin_login.login("Teliour", "367/qwQf22")

    admin_category.open()
    admin_category.create_category("Devices", "Category for devices")

    admin_product.open()
    products_to_add = [
        ("Mouse A", "Devices"),
        ("Mouse B", "Devices"),
        ("Keyboard A", "Devices"),
        ("Keyboard B", "Devices"),
    ]
    for name, category in products_to_add:
        admin_product.add_product(name, category, f"Description for {name}")

    main_page.open()
    for name, _ in products_to_add:
        main_page.search_product(name)
        time.sleep(1)
        product_link = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, name))
        )
        logger.info(f"Товар '{name}' найден на главной странице")

    admin_product.open()
    admin_product.delete_product_by_name("Mouse A")
    admin_product.delete_product_by_name("Keyboard A")

    remaining_products = ["Mouse B", "Keyboard B"]
    removed_products = ["Mouse A", "Keyboard A"]

    main_page.open()
    for name in remaining_products:
        main_page.search_product(name)
        time.sleep(1)
        product_link = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, name))
        )
        logger.info(f"Оставшийся товар '{name}' найден на главной странице")

    for name in removed_products:
        main_page.search_product(name)
        time.sleep(1)
        elements = driver.find_elements(By.LINK_TEXT, name)
        assert len(elements) == 0, f"Удалённый товар '{name}' найден на главной странице"
        logger.info(f"Удалённый товар '{name}' не найден на главной странице, как и ожидалось")

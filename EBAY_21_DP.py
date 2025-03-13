import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProductCollectorAI:
    def __init__(self, driver_path):
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=service, options=options)
        
        self.base_screenshot_dir = "product_screenshots"
        os.makedirs(self.base_screenshot_dir, exist_ok=True)
    
    def go_to_ebay(self):
        self.driver.get("https://www.ebay.com/")
        time.sleep(2)
    
    def explore_main_categories(self, start_index=5, end_index=12):
        for i in range(start_index, end_index):
            xpath = f'//*[@id="vl-flyout-nav"]/ul/li[{i}]'
            try:
                category_element = self.driver.find_element(By.XPATH, xpath)
                category_text = category_element.text.strip()
                print(f"[INFO] Ana kategoriye tıklanıyor: {category_text}")
                category_element.click()
                time.sleep(2)
                
                self.explore_sub_categories()
                
                self.driver.back()
                time.sleep(2)
            except NoSuchElementException:
                print(f"[WARNING] Kategori (li[{i}]) bulunamadı.")
                break
            except ElementClickInterceptedException:
                print(f"[WARNING] Kategoriye (li[{i}]) tıklanamadı.")
                break
    
    def explore_sub_categories(self, start_index=1, max_attempts=10):
        for i in range(start_index, start_index + max_attempts):
            sub_xpath = f'/html/body/div[2]/div[2]/section[2]/section[1]/div/ul/li[{i}]'
            try:
                sub_cat_element = self.driver.find_element(By.XPATH, sub_xpath)
                sub_cat_text = sub_cat_element.text.strip()
                print(f"    [INFO] Alt kategoriye tıklanıyor: {sub_cat_text}")
                sub_cat_element.click()
                time.sleep(2)
                
                self.explore_deeper_categories()
                
                product_count = self.get_product_count()
                print(f"    [INFO] Bu alt kategoride {product_count} ürün tespit edildi.")
                if product_count > 0:
                    self.scrape_products()
                else:
                    print("    [INFO] Ürün bulunamadı, devam ediliyor.")
                
                self.driver.back()
                time.sleep(2)
                
                self.scroll_down_a_bit()
                self.check_and_click_more_button()
                
            except NoSuchElementException:
                print("    [WARNING] Daha fazla alt kategori bulunamadı.")
                break
            except ElementClickInterceptedException:
                print("    [WARNING] Alt kategoriye tıklanamadı.")
                break
    
    def explore_deeper_categories(self, start_index=3, max_attempts=50):
        for i in range(start_index, start_index + max_attempts):
            deeper_xpath = f'/html/body/div[2]/div[2]/section[2]/section[1]/div/ul/li/section/div/ul/li[{i}]'
            try:
                deeper_elem = self.driver.find_element(By.XPATH, deeper_xpath)
                deeper_text = deeper_elem.text.strip()
                print(f"        [INFO] Daha derin kategori bulundu: {deeper_text}")
            except NoSuchElementException:
                break
    
    def get_product_count(self):
        try:
            return len(self.driver.find_elements(By.CSS_SELECTOR, "li.brwrvr__item-card.brwrvr__item-card--list"))
        except Exception:
            return 0
    
    def scrape_products(self):
        count = self.get_product_count()
        if count == 0:
            return
        
        product_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.brwrvr__item-card.brwrvr__item-card--list")
        if not product_elements:
            return
        
        products_data = []
        for idx, product in enumerate(product_elements, start=1):
            try:
                container = product.find_element(By.XPATH, "./div/div/div[2]")
                container_text = container.text.strip()
                
                if "sold" not in container_text.lower():
                    continue
                
                self.scroll_to_element(product)
                screenshot_path = self.take_product_screenshot(product, idx)
                
                products_data.append({
                    "full_text": container_text,
                    "screenshot_path": screenshot_path
                })
            except Exception as e:
                print(f"    [WARNING] Ürün {idx} işlenirken hata: {str(e)}")
        
        if products_data:
            filename = f"products_{int(time.time())}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(products_data, f, ensure_ascii=False, indent=2)
            print(f"    [INFO] {len(products_data)} ürün kaydedildi: {filename}")

    def smooth_scroll(self):
        scroll_pause_time = 0.5
        screen_height = self.driver.execute_script("return window.innerHeight")
        scroll_amount = screen_height * 0.8
        
        for i in range(5):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(scroll_pause_time)

    def scroll_down_a_bit(self):
        self.driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(1)

    def scroll_to_element(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        time.sleep(1)

    def check_and_click_more_button(self):
        try:
            more_button_xpath = '/html/body/div[2]/div[2]/section[2]/section[1]/div/div/button'
            more_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, more_button_xpath))
            )
            
            button_text = more_button.text.strip().lower()
            
            if "more" in button_text and more_button.is_displayed() and more_button.is_enabled():
                print(f"    [INFO] 'Load More' butonu bulundu ({button_text}), tıklanıyor...")
                more_button.click()
                time.sleep(2)
            else:
                print(f"    [INFO] Buton tıklanabilir durumda değil veya metin 'More' içermiyor: {button_text}")
                
        except NoSuchElementException:
            pass
        except ElementClickInterceptedException:
            print("    [WARNING] 'Load More' butonuna tıklanamadı.")
        except Exception as e:
            print(f"    [ERROR] Buton kontrolünde beklenmeyen hata: {str(e)}")

    def take_product_screenshot(self, product_element, index):
        try:
            unique_id = f"{int(time.time())}_{index}"
            product_dir = os.path.join(self.base_screenshot_dir, unique_id)
            os.makedirs(product_dir, exist_ok=True)
            
            screenshot_path = os.path.join(product_dir, "product_screenshot.png")
            product_element.screenshot(screenshot_path)
            
            return screenshot_path
        except Exception as e:
            print(f"    [ERROR] Ekran görüntüsü alma hatası: {str(e)}")
            return None
    
    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    driver_path = "/Users/ayberkturk/Desktop/chromedriver-mac-arm64-2/chromedriver"
    collector = ProductCollectorAI(driver_path=driver_path)
    
    collector.go_to_ebay()
    collector.explore_main_categories(start_index=3, end_index=12)
    collector.close()
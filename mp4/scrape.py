import pandas as pd
from selenium.webdriver.common.by import By
import time
import requests
from io import StringIO

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ 
        Leave this method as is! It will be over-written in the child classes
        Each child class should perform the following:
            Record the node value in self.order AND return its children
            parameter: node
            return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited = set()
        self.order = []
        self.dfs_visit(node)

    def dfs_visit(self, node):
        if node in self.visited:
            return
        
        self.visited.add(node)

        children = self.visit_and_get_children(node)

        for child in children:
            self.dfs_visit(child)
            
    def bfs_search(self, node):
        
        self.visited = set()
        self.order = []
        
        queue = [node]
        self.visited.add(node)
        
        while queue:
            
            current_node = queue.pop(0)
            children = self.visit_and_get_children(current_node)
            
            for child in children:
                if child not in self.visited:
                    self.visited.add(child)
                    queue.append(child)
        

class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def visit_and_get_children(self, node):
        self.order.append(node)

        children = []
        for child_node, has_edge in self.df.loc[node].items():
            if has_edge == 1:
                children.append(child_node)
        return children


class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        
    def visit_and_get_children(self, node):
        with open(f"file_nodes/{node}", "r") as file:
            value = file.readline().strip()
            children = file.readline().strip().split(",")
            
        self.order.append(value)
        return children
        
    
    def concat_order(self):
        return "".join(self.order)
    
    
class WebSearcher(GraphSearcher):
    
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.tables = []
        
    def visit_and_get_children(self, url):
        
        self.driver.get(url) 
        children = []
        
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        
        for link in links:
            href = link.get_attribute('href')
            if href:
                children.append(href)
                
        tables = pd.read_html(StringIO(self.driver.page_source))
        non_empty_tables = [table for table in tables if not table.empty]
        
        self.tables.extend(non_empty_tables)
        self.order.append(url)
        
        return children
    
    def table(self):
        
        if not self.tables:
            return pd.DataFrame() 
        
        return pd.concat(self.tables, ignore_index=True)
    
    
def reveal_secrets(driver, url, travellog):
    
    password = "".join(travellog["clue"].astype(str))
    
    driver.get(url)
    
    password_input = driver.find_element(By.ID, "password-textbox")
    password_input.send_keys(password)
    
    submit_button = driver.find_element(By.ID, "submit-button")
    submit_button.click()
    
    time.sleep(1)
    
    view_location_button = driver.find_element(By.ID, "location-button")
    view_location_button.click()
    
    time.sleep(1)
    
    image = driver.find_element(By.TAG_NAME, "img")
    image_link = image.get_attribute("src")
    
    response = requests.get(image_link)
    
    if response.status_code == 200:
        with open("Current_Location.jpg", "wb") as f:
            f.write(response.content)
            
    location_element = driver.find_element(By.ID, "location")
    current_location = location_element.text
    
    return current_location

        
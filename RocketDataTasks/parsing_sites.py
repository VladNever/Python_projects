import requests
from bs4 import BeautifulSoup
import json

class BaseOffice:
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0', }
        self.office_details = {
            "address": '',
            "latlon": '',
            "name": '',
            "phones": '',
            "working_hours": ''
            }
        self.list_offices = []

class FurnitureOffice(BaseOffice):
    def get_list_furn_offices(self):
        url =  self.url  
        headers = self.headers
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        office_list = soup.find_all('div', class_ = 'shop-list-item')
        for office in office_list:
            office = office.attrs
            self.office_details['address'] = office['data-shop-address']
            self.office_details['latlon'] = [office['data-shop-latitude'], office['data-shop-longitude']]
            self.office_details['name'] = office['data-shop-name']
            self.office_details['phones'] = office['data-shop-phone']
            self.office_details['working_hours'] = [office['data-shop-mode1'], office['data-shop-mode2']]
            self.list_offices.append(self.office_details)

class TourOffice(BaseOffice):
    @staticmethod
    def get_time_work(self, hoursofoperations):
        time_work = {}
        for key, value in hoursofoperations.items():          
            if value['isDayOff'] == True:
                hoursofoperations[key] = 'выходной'
            else:
                hoursofoperations[key] = value['startStr'] + ' до ' + value['endStr']
        time_work['пн - пт'] = hoursofoperations['workdays']
        time_work['сб'] = hoursofoperations['saturday']
        time_work['вс'] = hoursofoperations['sunday']    
        return time_work
        
    def get_list_tour_offices(self):
        headers = self.headers
        for cityid in range(1, 500):
            url =  self.url + str(cityid)
            print(url + ' city parsed')
            office_list = requests.get(url, headers=headers)
            office_list = office_list.json()['offices']
            for office in office_list:
                self.office_details['address'] = office['address']
                self.office_details['latlon'] = [office['latitude'], office['longitude']]
                self.office_details['name'] = office['name']
                self.office_details['phones'] = office['phone']
                self.office_details['working_hours'] = self.get_time_work(self, office['hoursOfOperation'])
                self.list_offices.append(self.office_details)
        print(str(len(self.list_offices)) + ' tour offices')

if __name__ == "__main__":
    furniture_url = 'https://www.mebelshara.ru/contacts'
    tour_url = 'https://apigate.tui.ru/api/office/list?cityId='

    furniture_offices = FurnitureOffice(furniture_url)
    furniture_offices.get_list_furn_offices()

    tour_offices = TourOffice(tour_url)
    tour_offices.get_list_tour_offices()

    offices_dict = {
        'furniture_offices': furniture_offices.list_offices,
        'tour_offices': tour_offices.list_offices
    }

    with open('offices.txt', 'w') as outfile:
        json.dump(offices_dict, outfile)

    # check json file
    # with open('offices.txt', 'rb') as fp:
    #     my_file_unstr = fp.read()
    #     my_file = json.loads(my_file_unstr)
    #     print(my_file)

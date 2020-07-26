#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from COVID_plots import *

country = "Switzerland"
provinces = []
plot_data(country = country, provinces = provinces)

country = "Hungary"
provinces = []
plot_data(country = country, provinces = provinces)

country = "Germany"
provinces = ["Nordrhein-Westfalen", "Bayern", "Baden-Wurttemberg"]
plot_data(country = country, provinces = provinces)

country = "US"
provinces = ["New York", "Florida", "Texas", "California", "Washington"]
plot_data(country = country, provinces = provinces)

country = "Spain"
provinces = ["Catalonia", "Madrid", "Aragon", "Canarias", "Baleares","Pais Vasco"]
plot_data(country = country, provinces = provinces)

country = "Japan"
provinces = ["Tokyo", "Ibaraki", "Kyoto", "Hokkaido", "Saitama"]
plot_data(country = country, provinces = provinces)

country = "South Africa"
provinces = []
plot_data(country = country, provinces = provinces)

country = "Canada"
#print_provinces(country)
provinces = ["Quebec", "Alberta", "British Columbia", "Ontario"]
plot_data(country = country, provinces = provinces)


#plot_all()


import pandas as pd
import xml.etree.ElementTree as ET

from constants import fuel_types

def xmls_to_df_dict(xmls, type):
  print(f"\tProcessing {type} data")

  data = { "Time": [], "UnitName": [], "Type": [], "quantity": [] }

  for xml in xmls:
    root = ET.fromstring(xml)
    namespace = { 'ns': root.tag.split('}', 1)[0][1:] }

    for time_series in root.findall('.//ns:TimeSeries', namespace):
      if type == 'generation':
        psr_type = time_series.find('ns:MktPSRType/ns:psrType', namespace).text
      unit_name = time_series.find('ns:quantity_Measure_Unit.name', namespace).text
      if unit_name != 'MAW':
        raise Exception(f"Unexpected unit: {unit_name}")
      for period in time_series.findall('ns:Period', namespace):
        start_time = pd.to_datetime(period.find('ns:timeInterval/ns:start', namespace).text)
        resolution = int(period.find('ns:resolution', namespace).text.replace('PT', '').replace('M', ''))
        for point in period.findall('ns:Point', namespace):
          position = int(point.find('ns:position', namespace).text)
          quantity = int(point.find('ns:quantity', namespace).text)
          data['Time'].append(start_time + pd.to_timedelta((position-1) * resolution, unit='m'))
          data['UnitName'].append(unit_name)
          data['Type'].append('load' if type == 'load' else psr_type)
          data['quantity'].append(quantity)
  
  return data_to_df_dict(data)

def jsons_to_df_dict(jsons, type):
  print(f"\tProcessing {type} data")

  data = { "Time": [], "UnitName": [], "Type": [], "quantity": [] }

  for json in jsons:
    if type == 'generation':
      for item in json:
        startTime = pd.to_datetime(item['startTime'])
        for generation_entry in item['data']:
          if fuel_types[generation_entry['fuelType']] == 'nil': continue
          data['Time'].append(startTime)
          data['UnitName'].append('MAW')
          data['Type'].append(fuel_types[generation_entry['fuelType']])
          data['quantity'].append(generation_entry['generation'])
    else:
      for item in json['data']:
        data['Time'].append(pd.to_datetime(item['startTime']))
        data['UnitName'].append('MAW')
        data['Type'].append('load')
        data['quantity'].append(item['initialDemandOutturn'])

  return data_to_df_dict(data)

def data_to_df_dict(data):
  # Convert the data dictionary into a pandas DataFrame
  df = pd.DataFrame(data)

  # Create a separate DataFrame for each type
  df_dict = { type: df[df["Type"] == type] for type in df["Type"].unique() }

  for type in df_dict:
    # set the index of the DataFrame to the Time column
    df_dict[type].set_index('Time', inplace=True)
    # drop duplicate rows
    df_dict[type] = df_dict[type][~df_dict[type].index.duplicated(keep='first')]

  return df_dict
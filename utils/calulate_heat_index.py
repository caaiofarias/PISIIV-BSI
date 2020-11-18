import json


def convertCtoF(temp):
    return (temp * 1.8) + 32


def convertFtoC(temp):
    return ((temp - 32) * 5) / 9


def calculate_heat_index(data):
  heat_index_list = []
  for i in range(len(data)):
    if(data[i]["TEM_MAX"] != None):
      temp_media = (convertCtoF(float(data[i]["TEM_MAX"])) + convertCtoF(float(data[i]["TEM_MIN"]))) / 2
      umd_media = ((float(data[i]["UMD_MAX"]) + float(data[i]["UMD_MIN"])) / 2) / 100
      heat_index = 1.1 * temp_media - 10.3 + 0.047 * umd_media
      if(heat_index < 80):
        heat_index_list.append(heat_index)
      else:
        heat_index = -42.379 + (2.04901523 * temp_media) + \
          (10.14333127 * umd_media) - (6.83783 * 10**-3) * temp_media**2 \
            - (5.481717 * 10 ** -2) * umd_media ** 2 + 1.22874 * (10 ** -3) \
              * (temp_media ** 2) * umd_media + 8.5282 * (10**-4) * temp_media \
                * umd_media ** 2 - (1.99 * 10**-6) * temp_media**2 * umd_media ** 2
        if(temp_media >= 80 and temp_media <= 112 and umd_media <= 0.13):
          heat_index = heat_index - (3.25 - (0.25 * umd_media)) \
            * ((17 - (abs(temp_media - 95))) / 17) ** 0.5
          heat_index_list.append(heat_index)
        else:
          if(temp_media >= 80 and temp_media <= 87 and umd_media > 0.85):
            heat_index = heat_index + 0.02 * \
              (umd_media - 85) * (87 - temp_media)
            # print(heat_index)
            heat_index_list.append(heat_index)
          else:
            # print(heat_index)
            heat_index = heat_index
            heat_index_list.append(heat_index)
    else:
      continue
  finalHI = 0.0
  finalHI = sum(heat_index_list)
  finalHI = "{:.1f}".format(convertFtoC(finalHI / len(heat_index_list)))
  heat_index_list.append(data[0]["DC_NOME"])
  final_temp = "{:.1f}".format(convertFtoC(temp_media))
  return {
    "station":data[0]["DC_NOME"],
    "hindex":finalHI,
    "temperatura":final_temp
    }

file = open('out.json', 'r')
data = []
for line in file:
    dic = json.loads(line)
    data.append(dic)
print(calculate_heat_index(data))
file.close()

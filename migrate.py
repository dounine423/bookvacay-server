from db import insertQuery,selectQuery
from bs4 import BeautifulSoup

# from  hotel.boards import boardTypes
# from hotel.facilities import facilities
# from hotel.categories import categories
# from hotel.facilityGroups import facilityGroups
# from hotel.imagetypes import imageTypes
# from hotel.groupCategories import groupCategories
# from hotel.promotions import promotions
# from hotel.segments import segments
# from hotel.terminals import terminals
# from hotel.issue import issue
# from hotel.currency import currency

# def insertBoard():
#     for board in boardTypes:
#         query=f"insert into board (code , languageCode, content, multiLingualCode ) values ( '{board['code']}' , '{board['description']['languageCode']}' ,'{board['description']['content']}' , '{board['multiLingualCode']}')"
#         InsertData(query)
#     print("success")

# def insertFacility():
#     for facility in facilities:
#         flag=facility.get('description')
#         languageCode=facility['description']['languageCode'] if flag != None else None
#         content=facility['description']['content'] if flag != None else None
#         query=f"insert into facility (code , facilityGroupCode , facilityTypologyCode , languageCode, content ) values ( '{facility['code']}' , '{facility['facilityGroupCode']}' , '{facility['facilityTypologyCode']}' , '{languageCode}' ,'{content}')"
#         InsertData(query)
#         # insert 2 code 105 111
#     print("success",len(facilities))

# def insertCategory():
#     print("success",len(categories))
#     for category in categories:
#         flag=category.get('description')
#         languageCode=category['description']['languageCode'] if flag!=None else None
#         content=category['description']['content'] if flag!=None else None
#         query=f"insert into category (code , simpleCode , accommodationType , groupName , languageCode, content ) values ( '{category['code']}' , '{category['simpleCode']}' , '{None}' , '{category.get('group')}' , '{languageCode}' ,'{content}')"
#         InsertData(query)

# def insertFacilityGroup():
#     print("success",len(facilityGroups))
#     for group in facilityGroups:
#         query=f"insert into facilityGroup (code , languageCode, content ) values ( '{group['code']}' , '{group['description']['languageCode']}' ,'{group['description']['content']}')"
#         InsertData(query)

# def insertImageType():
#     print("success",len(imageTypes))
#     for type in imageTypes:
#         query=f"insert into imageType (code , languageCode, content ) values ( '{type['code']}' , '{type['description']['languageCode']}' ,'{type['description']['content']}')"
#         InsertData(query)

# def insertGroupCategory():
#     print("success",len(groupCategories))
#     for group in groupCategories: 
#         query=f"insert into groupCategory (code , rank ,  languageCode, name ,  description ) values ( '{group['code']}' , '{group['order']}' , '{group['name']['languageCode']}' ,'{group['name']['content']}', '{group['description']['content']}')"
#         InsertData(query)

# def insertPromotion():
#     print("success",len(promotions))
#     for group in promotions:
#         flag=group.get('description')
#         description= group['description']['content'] if flag !=None else None
#         query=f"insert into promotion (code ,  languageCode, name ,  description ) values ( '{group['code']}' ,   '{group['name']['languageCode']}' ,'{group['name']['content']}', '{description}')"
#         InsertData(query)

# def insertSegment():
#     print("success",len(segments))
#     for type in segments:
#         query=f"insert into segment (code , languageCode, content ) values ( '{type['code']}' , '{type['description']['languageCode']}' ,'{type['description']['content']}')"
#         InsertData(query)

# def insertTerminal():
#     print("success",len(terminals))
#     for group in terminals:
#         query=f"insert into terminal (code ,type, country, languageCode, name ,  description ) values ( '{group['code']}' ,'{group['type']}', '{group['country']}',  '{group['name']['languageCode']}' ,'{group['name']['content']}', '{group['description']['content']}')"
#         InsertData(query)

# def insertIssue():
#     print("success",len(issue))
#     for group in issue:
#         flag=group.get('description')
#         description='"'+ group['description']['content']+'"' if flag !=None else None
#         languageCode=group['description']['languageCode'] if flag != None else None
#         flag=group.get('name')
#         name='"'+ group['name']['content'] + '"' if flag != None else None
#         query=f"insert into issue (code , type , languageCode, name ,  description, alternative ) values ( '{group['code']}' , '{group.get('type')}' , '{languageCode}' ,{name}, {description} ,'{group.get('alternative')}')"
#         InsertData(query)

# def insertCurrency():
#     print("success",len(currency))
#     for group in currency:
#         query=f"insert into currency (code ,type , languageCode, content ) values ( '{group['code']}' ,'{group['currencyType']}', '{group['description']['languageCode']}', '{group['description']['content']}')"
#         InsertData(query)

# def insertDestination():
#     print("success",len(destinations))
#     for group in destinations:
#         query=f"insert into destination (code , name ) values ( '{group['code']}' , '{group['name']}')"
#         InsertData(query)

def changeCurrency():
    html_doc=""
    currency=[]
    with open('currency.html','r') as f:
        html_doc=f.read()
    soap=BeautifulSoup(html_doc,'html.parser')
    result= soap.find_all('div',attrs={'class':'ea1163d21f'})
    for item in result:
        value=item.find('font').text
        value=value.strip()
        if value =='HOOK':
            currency.append('HUK')
        else:
            currency.append(value)
    where=f" code = '{currency[0]}' "
    for item in currency:
        where+=f" or  code = '{item}' "
    select=" code , content"
    table="currency2"
    tempCurrency=selectQuery(select,table,where)
    field=" code, content"
    for item in tempCurrency:
        # print(item[1])
        value=f" '{item[0]}', '{item[1]}'"
        insertQuery('currency',field,value)
    print("success")



    


def main():
    changeCurrency()

if __name__ == "__main__":
    main()
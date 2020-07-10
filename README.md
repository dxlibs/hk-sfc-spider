# Hongkong SFC Spider

Hongkong SFC spider crawler the public information on the website of Hongkong's Securities and Futures Commission.

[Official Website of SFC](https://www.sfc.hk/web/EN/index.html)

#### environment
- Python 3, it's very easy transfer into Python 2
- MySQL

#### requirements
- nothing special


### step 1
run function multi_process_user in main.py to get all ceref code
```python
def multi_process_user(type):
    letters = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
        'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
    ]
    for role in ['individual', 'corporation']:
        for letter in letters:
            get_user(role, type, letter, 1)
```

### step 2
get corporations and individuals details info pages
```python
def multi_process_page(type, file_id):
    page_indi = ['indi_details', 'indi_addresses', 'indi_conditions', 'indi_disciplinaryAction', 'indi_licenceRecord']
    page_corp= ['corp_details', 'corp_addresses', 'corp_ro', 'corp_rep', 'corp_co', 'corp_conditions', 'corp_da', 'corp_prev_name', 'corp_licences']
    pages = page_indi if type == 'indi' else page_corp
    file = PROJECT_ROOT + '/user/{}_{}.txt'.format(type, file_id)
    with open(file, 'r') as fp:
        for line in fp.readlines():
            ceref = line.strip()
            for page in pages:
                get_page(ceref, page, file_id)
```

### step 3
parse pages HTML in parse.py

### End
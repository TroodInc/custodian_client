# Custodian API Python Client


## Client instantiation

To start using client just instantiate it like in the following snippet: 

    from custodian.client import Client
    client = Client('http://localhost:8080/custodian/', authorization_token="c4216a3440b04270945d2b69ed2d4365")

Custodian Server`s URL is required, Trood Auth authorization token is optional.


## Working with objects
### Instantiating object
To instantiate new Custodian object use *Object* class.


##### Arguments:
+   name:str - object`s name
+   cas:bool - cas flag
+   objects_manager: ObjectsManager - ObjectsManager instance
+   key:str - primary key field name
+   fields: List[BaseField] - a list of fields

##### Usage example:
    from custodian.objects import Object
    
    account_obj = Object(
            name='account',
            fields=[NumberField(name='id'), NumberField(name='balance'), StringField(name='owner')],
            key='id',
            cas=False,
            objects_manager=client.objects
        )

#### Object`s laziness
Object can be instantiated lazily, meaning its key and fields will be synced with the Custodian only when accessing 
this attributes.  


### Object`s fields
Fields are available at *custodian.objects.fields* module:
+  NumberField
+  IntegerField
+  StringField
+  BooleanField
+  ArrayField
+  ObjectField
+  DateField
+  TimeField
+  DateTimeField

### Object operations
All Custodian object-related operations are performed using ObjectsManager which is available via client instance as 
*objects* attribute.

### CRUD-operations
### List objects
To get all objects from the Custodian use *get_all* method:

##### Arguments: -
##### Returns: List[Object]
##### Usage example:
```
client.objects.get_all()
```

### Creating object
To create a new object use *create* method:

##### Arguments: object:Object
##### Returns: Object
##### Usage example:
```
obj = client.objects.create(obj)
```

### Updating object
To update an existing object use *update* method:

##### Arguments: object:Object
##### Returns: Object
##### Usage example:
```
obj = client.objects.update(obj)
```


### Deleting object
To delete an existing object from the Custodian use *delete* method:

##### Arguments: object:Object
##### Returns: :Object
##### Usage example:
```
client.objects.delete(obj)
```

## Working with records
All record-related operations are performed using RecordsManager which is available via client instance as 
*records* attribute.


### Instantiating record
To create a new record instance use *Record* class. 
 
##### Arguments:
+   obj:Object - Object instance
+   **values - Record values, only values listed in the obj.fields will be assigned as record values.   

##### Usage example:
    from custodian.records.models import Record
    
    account_record = Record(
            obj=account_obj,
            balance=4900,
            number=58812409,
            owner='Sergey Petrov'
        )

## Single CRUD operations
### Creating new record
To create a new record in the Custodian use *create* method:

##### Arguments:
+   record:Record - a Record instance to create

##### Returns: Record 

##### Usage example:
    account_record = client.records.create(account_record)

### Updating existing record
To update an existing record in the Custodian use *update* method:

##### Arguments:
+   record:Record - a Record instance to create

##### Returns: Record 

##### Usage example:
    account_record = client.records.update(account_record)


### Deleting existing record
To delete an existing record from the Custodian use *delete* method:

##### Arguments:
+   record:Record - a Record instance to create

##### Returns: Record 

##### Usage example:
    client.records.delete(account_record)

## Bulk CRUD operations
### Creating new records
To create a list of new records in the Custodian use *bulk_create* method:

##### Arguments:
+   *records:Record - a Record instances to create

##### Returns: List[Record] 

##### Usage example:
    account_records = client.records.bulk_create(account_record, another_account_record)

### Updating existing records
To update a list of existing records in the Custodian use *bulk_update* method:

##### Arguments:
+   *records:Record - a Record instances to update

##### Returns: List[Record] 

##### Usage example:
    account_records = client.records.bulk_update(account_record, another_account_record)


### Deleting existing records
To delete a list of existing records from the Custodian use *bulk_delete* method:

##### Arguments:
+   *records:Record - a Record instances to delete

##### Returns: List[Record] 

##### Usage example:
    client.records.bulk_delete(account_record, another_account_record)

## Making queries
Querying consists of two steps: getting Query instance and applying filters to it.
  
### Getting Query instance
To get the *Query* instance use *query* method.

##### Arguments:
+   obj:Object - an Object instance for which the querying will be made.

##### Returns: Query 

##### Usage example:
    query = client.records.query(account_obj)

Now you can make queries.
### Filtering records
To specify filtering options use *filter* method. It receives both optional *Q* instance and filters. 
Filter name should be in the following format:
    
    <field_name>__<operator>
    
Operator should be one of the RQL`s standard operator: https://doc.apsstandard.org/7.1/api/rest/rql/#relational-operators 

##### Arguments:
+   q_object:Q - Q instances to apply to the query
+   **filters - filters to apply to the query 

##### Returns: Query 

##### Usage example:
    sergey_accounts = client.records.query(account_obj).filter(owner='Sergey Petrov')

#### What is Q
Q is an logical expression, which is used to assemble more complex expressions using 
"|"(OR), "&"(AND) and "~"(NOT) operators. 
Its functionality is equivalent to the Django`s Q.
##### Usage example:
    name_expression = Q(owner='Nikolai Kozlov') | Q(owner='Sergey Petrov') # get all Nikolai`s and Sergey`s accounts
    balance_expression = Q(balance__gt=0) # with positive balance
    accounts = client.records.query(account_obj).filter(name_expression & balance_expression)

### Ordering records
To set ordering for the query use *order_by* method. To set ASC ordering just use field name, to set DESC ordering 
predicate field name with "-" symbol. 
    
    
##### Arguments:
+   *orderings:str - orderings for the query 

##### Returns: Query 

##### Usage example:
    accounts = accounts.order_by('owner', '-balance')

### Using offset and limit
*Query* objects are lazy and evaluation is done only when its records are retrieved. So effective work with records can 
be done using *offset* and *limit* options. Just like with Django ORM, you should use list slices to define this options.


##### Usage example:
    accounts_slice = accounts.order_by('owner', '-balance')[100:150] # gets 50 records starting with 100
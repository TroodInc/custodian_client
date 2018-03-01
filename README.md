# Custodian API Python Client


## Client instantiation

To start using client just instantiate it like in the following snippet: 
```
client = Client('http://localhost:8080/custodian/')
```
The only argument is Custodian Server`s URL.


## Working with objects
### Instantiating object
To instantiate new Custodian object use Object class.

###### Arguments:
+   name:str - object`s name
+   cas:bool - cas flag
+   objects_manager: ObjectsManager - ObjectsManager instance
+   key:str - primary key field name
+   fields: List[BaseField] - a list of fields

###### Usage example:
    
    obj = Object(
            name='account',
            fields=[NumberField(name='id'), StringField(name='number')],
            key='id',
            cas=False,
            objects_manager=client.objects
        )

All Custodian object-related operations are performed using ObjectsManager which is available via client instance as 
*objects* attribute.

### CRUD-operations
### List objects
To get all objects from the Custodian use *get_all* method:

###### Arguments: -
###### Returns: List[Object]
###### Usage example:
```
client.objects.get_all()
```

### Creating object
To create a new object use *create* method:

###### Arguments: object:Object
###### Returns: Object
###### Usage example:
```
obj = client.objects.create(obj)
```

### Updating object
To update an existing object use *update* method:

###### Arguments: object:Object
###### Returns: Object
###### Usage example:
```
obj = client.objects.update(obj)
```


### Deleting object
To delete an existing object use *delete* method:

###### Arguments: object:Object
###### Returns: Object
###### Usage example:
```
obj = client.objects.delete(obj)
```



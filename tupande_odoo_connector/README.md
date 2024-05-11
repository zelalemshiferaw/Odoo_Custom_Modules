
# Tupande odoo connector

We recived the endpoint from Tupande as json and based upon the paramerters we create the sale order and client on odoo.

# Tech Stack

Languages Used: Python, XML

Technologies Used: Python 3, Odoo v14

Developed For: Odoo v14

# Sale order Functionality

    Create Sale Order Management: Creates new Sale order records in Odoo if they don't already exist.
    Unique Identifier Handling for Sale order is tupande_sale_ref as a mandatory key for accurate message processing.
    Update Sale Order Management: update sale order records in Odoo if they exist base upon tupande_sale_ref.
    If sale order is not fulfill then we can update all order else we can't 

## Client Functionality

    Create Client Order Management: Creates new client records in Odoo if they don't already exist.
    Unique Identifier Handling for client is tupande_client_id as a mandatory key for accurate message processing. we can create multiple client on the same time.
    Update Client Order Management: update sale order records in Odoo if they exist base upon tupande_client_id.
    We can update multiple client on the same time.

## API Reference

### Get client data

  `GET /tupande/clinet`

| Parameter | Type     | Description                                         |
|-------------|---------|--------------------------------------------------|
| `id` | `string` | **Required**. tupande client ID                     |
| `firstName` | `string` | **Required**. client firstName                      |
| `lastName` | `string` | **Required**. Client lastName                       |
| `phoneNumber` | `string` | **Required**. Client phoneNumber                    |
| `gender` | `string` | Gender (Male, Female)                               |
| `dob` | `string` | Client Date of birth                                |
| `nid` | `string` | national Id number of client                        |
| `age` | `string` | Clinet age like '18 - 25', '26 - 30', '26 - 30' etc |

#### Get order data

    `GET /tupande/order`

| Parameter | Type     | Description                                                   |
| :-------- | :------- |:--------------------------------------------------------------|
| `clientId` | `string` | **Required**. tupande client ID                               |
| `firstName` | `string` | **Required**. client first name key                           |
| `lastName`  | `string`| **Required**. Client's last name key                          |
| `phoneNumber` | `string` | **Required**. Client phone key                          |
| `orderDate` | `string` | Sale order Date key                                           |
| `shopId` | `string` | **Required**. Shop id of odoo                                 |
| `chanalId` | `string` | **Required**. Chanal id of odoo                               |
| `orderRef` | `string` | **Required**. Sale order Reference number key                 |
| `amountTotal` | `string` | **Required**. Sale Order Total Amount                         |
| `orderLines` | `list` | **Required**. Sale order line [product_name, qty, unit_price] |

## Appendix

We can able to create and as well update sale order if any fulfillemt is not done.
Similarly we can able to create and update client singuler and bulk as well.

## Testing

To run the tests for this module, run the following command:

    ./odoo-bin -c {path/to/odoo.conf} -d {db_name} -i tupande_odoo_connector --test-enable --stop-after-init

## Authors

- [@Usman](https://www.github.com/usmanjoiya)
Sync Product from tupande to Odoo

---------------------------------------

We want to create client from tupande to odoo and it can be on bulk as well single.
I create only one end point for all of these options
1- Create/Update single Client
2- Create/Update Bulk Client

# Create/Update single Client

---------------------------------;

We received Json format like below and it's either create or update client
  {
    "id":"222",
    "firstName": "John",
    "lastName": "Doe",
    "gender": "Male",
    "verified": "false",
    "nid": "xxxx-xxx-xxx",
    "phoneNumber": "+25478398xxx22222"
  }

Case-1
If client not exist we create and assign tupande_client_id

Case-2
If phone number already exist we assign tupande_client_id with that client

Case-3
If tupande_client_id already exist we update all it's parameters

# Create/Update bulk Client

----------------------------------;

We received list of dictionary format like below and it's either create or update client
  [{
    "id":"222",
    "firstName": "John",
    "lastName": "Doe",
    "gender": "Male",
    "verified": "false",
    "nid": "xxxx-xxx-xxx",
    "picture": "http://localhost:8060/web/image?model=res.partner&id=26&field=image_128&unique=02292024233926",
    "phoneNumber": "+25478398xxx22222"
  },
    {
    "id":"333",
    "firstName": "John-1",
    "lastName": "Doe-1",
    "gender": "Male",
    "verified": "false",
    "nid": "xxxx-xxx-xxx",
    "picture": "http://localhost:8060/web/image?model=res.partner&id=26&field=image_128&unique=02292024233926",
    "phoneNumber": "+25478398xxx333"
  },
    {
    "id":"444",
    "firstName": "John-3",
    "lastName": "Doe-3",
    "gender": "Male",
    "verified": "false",
    "nid": "xxxx-xxx-xxx",
    "picture": "http://localhost:8060/web/image?model=res.partner&id=26&field=image_128&unique=02292024233926",
  },
  ]

It always shows 200 response but a list of dictionary

Response 200 and the reason is if one client fails based on that i can't stop the whole process
[{
    'httpStatusCode': '200',
    'id': 222,
    'odoo-id': 456,
    'message': "Client Details updated successfully"
},
{
    'httpStatusCode': '201',
    'id': 333,
    'odoo-id': 457,
    'message': "Client created successfully on odoo"
},
{
    'httpStatusCode': '400',
    'id': 444,
    'odoo-id': False,
    'message': "Phone Number is required and not received"
}
]

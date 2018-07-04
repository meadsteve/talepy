Tale Distributed Transactions
------------------------------

[![Build Status](https://travis-ci.org/meadsteve/talepy.svg?branch=master)](https://travis-ci.org/meadsteve/talepy)

## What?
Tale is a small library to help write a "distributed transaction like" 
object across a number of services. It's loosely based on the saga pattern.
A good intro is available on the couchbase blog: 
https://blog.couchbase.com/saga-pattern-implement-business-transactions-using-microservices-part/

## Installation
```bash
pipenv install talepy
```

## Example Usage
An example use case of this would be some holiday booking software broken
down into a few services.

Assuming we have the following services: Flight booking API, Hotel booking API, 
and a Customer API.

We'd write the following steps:

```python
from talepy.steps import Step

class DebitCustomerBalance(Step):

    def __init__(self):
        self.payment_client= {}

    def compensate(self, state):
        state['payment_id'] = self.payment_client.bill(state.customer_id, state.payment_amount)
        return state
        
    def execute(self, state):
        self.payment_client.refund(state['payment_id'])
       
```

and so on for any of the steps needed. Then in whatever is handling the user's 
request a distributed transaction can be built:

```python
from talepy import run_transaction

run_transaction(
    steps=[
        DebitCustomerBalance(), 
        BookFlight(), 
        BookHotel(), 
        EmailCustomerDetailsOfBooking()
    ],
    starting_state={}
)
```

If any step along the way fails then the compensate method on each step
is called in reverse order until everything is undone.

## Testing / Development
TODO
# Tale Distributed Transactions

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

    def execute(self, state):
        state['payment_id'] = self.payment_client.bill(state.customer_id, state.payment_amount)
        return state
        
    def compensate(self, state):
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

### Steps as Lambdas

For some cases you may not want to create a class for the step. Lambdas can be used directly 
instead. Extending the previous example:

```python
from talepy import run_transaction

run_transaction(
    steps=[
        DebitCustomerBalance(), 
        BookFlight(),
        lambda _: print("LOG -- The flight has been booked"),
        BookHotel(), 
        EmailCustomerDetailsOfBooking()
    ],
    starting_state={}
)
```

This new print statement will now execute following a success in `BookFlight`. 

It's also possible to implement compensations by adding another lambda as a tuple pair:

```python
from talepy import run_transaction

run_transaction(
    steps=[
        DebitCustomerBalance(), 
        BookFlight(),
        (
            lambda _: print("LOG -- The flight has been booked"), 
            lambda _: print("LOG -- ┌[ ಠ ▃ ಠ ]┐ something went wrong")
        ),
        BookHotel(), 
        EmailCustomerDetailsOfBooking()
    ],
    starting_state={}
)
```

### Automatic retries

You may also want to try a step a few times before giving up. A continence
function is provided to help out with this. Starting with the initial example.
If the hotel booking step is a bit unreliable and we want to try it 3 times:

```python
from talepy import run_transaction
from talepy.retries import attempt_retries

run_transaction(
    steps=[
        DebitCustomerBalance(), 
        BookFlight(),
        attempt_retries(BookHotel(), times=2), 
        EmailCustomerDetailsOfBooking()
    ],
    starting_state={}
)
```

The book hotel step will now be executed 3 times before the transaction is aborted. Once
all these attempts fail the normal compensation logic will be applied.

### Async

If you want to make use of `async` in your steps you can use `run_async_transaction`
instead. This behaves slightly differently to `run_transaction` as the ordering
of the steps isn't guaranteed. This means all steps receive the same starting state.

```python
from talepy.parallel import run_async_transaction
from talepy.steps import Step

class AsyncBookFlight(Step):

    async def execute(self, state):
        # do something
        return state
        
    async def compensate(self, state):
        # revert something
        pass
       

await run_async_transaction(
    steps=[
        DebitCustomerBalance(), 
        AsyncBookFlight(),
        EmailCustomerDetailsOfBooking()
    ],
    starting_state={}
)
```

## Testing / Development
TODO
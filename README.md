# Package delivery routing optimization

<img width="640" src="https://github.com/pettod/delivery-routing/assets/33998401/60a148f3-8172-4861-82a9-6a31ae8ff400">

## Introduction

Using [Google OR Tools](https://developers.google.com/optimization/introduction) to optimize Vehicle Routing Problem with constraints. The constraints are as follows:

- Minimize traveling distance
- N number of vehicles
- M number of packages
- Delivery deadlines of the packages
- Driver's working hours
- Driver's maximum single delivery distance
- Driver's mandatory lunch break

The codes assume the delivery takes 1 time unit per one distance unit. For example, an 8 hour work day would result in 60*8=480 constraint of the maximum total delivery distance.

## Installation

```bash
pip install -r requirements.txt
```

## Examples

### 1 delivery vehicle, 30 packages

![Figure_3](https://github.com/pettod/delivery-routing/assets/33998401/a6ed21a6-32eb-4712-9333-0518d4fae30d)

### 1 delivery vehicle, 300 packages

![Figure_4](https://github.com/pettod/delivery-routing/assets/33998401/092c136d-3b3f-4182-94f1-c7f47ee4615e)

### 4 delivery vehicles, 30 packages

![Figure_2](https://github.com/pettod/delivery-routing/assets/33998401/df0e5855-92e8-4064-a09c-1cdd3b507e50)

### 4 delivery vehicles, 300 packages

![Figure_1](https://github.com/pettod/delivery-routing/assets/33998401/79be6ee3-585d-4e3a-813c-3bce5107f1b0)

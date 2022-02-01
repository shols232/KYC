# KYC
KYC is an abbreviation for Know Your Customer. Gives an organization the ability to verify a person is who they say they are.
This software integrates BVN matching with multiple providers and cascades through all until one succeeds.

## Readme Notes

* Always run docker commands with user priviledges. not root.


## Retrieve code

* `$ git clone https://github.com/shols232/KYC.git`
* `cd kyc`


## Installation

* Install [docker](https://docs.docker.com/engine/install/) and
* Install [docker-compose](https://docs.docker.com/compose/install/)
* Make sure you can [run docker as non-sudo](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)

## Running

### Start up the backend containers
* `$ docker-compose up`

## Testing

* `$ docker exec -it kyc_web_1 poetry run py.test -W error::RuntimeWarning  tests/` 

## Notes:
All API Routes can be found at `$BASE_URL/api/docs/redoc/`

## Images of API
![kyc_validate_1](https://user-images.githubusercontent.com/62092484/151929027-dc82b26f-d79e-4c70-b98b-405f9446b136.png)


# Radar warning for HomeAssistant

[![release][release-badge]][release-url]
![downloads][downloads-badge]
[![PayPal.Me][paypal-me-badge]][paypal-me-url]
[![BuyMeCoffee][buy-me-a-coffee-shield]][buy-me-a-coffee-url]


Radar warning integration for HomeAssistant  

## Introduction

*This integration has not yet been tested and is in beta phase*

I give no guarantee for the functionality and no promise of lifelong maintenance, as I do the whole thing in my free time. Of course, I am happy about every contribution and PR.

This integration enables the detection and display of mobile speed cameras or radar traps within a specified radius around a given latitude and longitude. The speed cameras or radar traps are dynamically shown on the standard Home Assistant (HA) map.

Additionally, with the use of the Google Geocoding API, formatted addresses of these radar traps are retrieved and displayed, offering precise location details. This enhances the overall user experience by providing both map visualizations and detailed address information within the monitored zone.

## Installation

### HACS

The Radar integeration is not available in [HACS][hacs] (Home Assistant Community Store) by default, but you can add it as custom repositories.

1. Install HACS if you don't have it already
2. Open HACS in Home Assistant 
3. Add this repository (https://github.com/MelleD/ha-radar-warning) via HACS Custom repositories ([How to add Custom Repositories](https://hacs.xyz/docs/faq/custom_repositories/))

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MelleD&repository=ha-radar-warning&category=plugin)

## Google Geocoding API Setup

The Google Geocoding API allows you to determine and process location data. This is optional and improves the adress data for the POIs. This guide outlines the steps to set up and use the Google Geocoding API.

### Prerequisites
- A Google Cloud account
- A Google Cloud project
- Access to the Google Cloud Console

### Step-by-Step Guide
#### 1. Create a Google Cloud Project
- Go to the Google Cloud Console.
- Click on the project dropdown menu at the top of the page and select "New Project".
- Enter a project name and billing account (if prompted), then click "Create".
- Make a note of your Project ID, as you'll need it later.

#### 2. Enable the Geocoding API
- In the Google Cloud Console, navigate to the "API & Services" section.
- Click on "Library" to view available APIs.
- Search for "Geocoding API" in the search bar.
- Click on "Geocoding API" and then click "Enable".

#### 3. Set Up Billing
Google Cloud requires billing information to use most of its APIs.

- In the Google Cloud Console, go to the "Billing" section.
- Link your project to a billing account if you haven't already done so.
#### 4. Create API Credentials
- In the Google Cloud Console, go to the "API & Services" > "Credentials" section.
- Click on "Create Credentials" and select "API Key".
- Copy the API key that is generated. You will need this key to authenticate your API requests and copy it to the config in HA.

#### ‼️ Danger ‼️
You can (currently) make 40.000 request per month for free. After that you have to pay for the request, but you can restrict your API key and setup alerting:
- In the Google Cloud Console, navigate to "API & Services" > "Dashboard".
- Here you can monitor your API usage and set up alerts if needed.
- To manage quotas, go to "API & Services" > "Quotas" and adjust your settings as necessary. e.g. 1250 request per day


## Support

Clone and create a PR to help make the card even better.

Please ⭐️ or sponsor this repo when you like it.

## Sponsor ❤️

<a href="" target="_blank"><img src="https://img.shields.io/static/v1.svg?label=%20&message=PayPal.Me&logo=paypal" alt="PayPal.Me MelleDennis" style="height: auto !important;width: auto !important;" ></a>

<a href="https://www.buymeacoffee.com/melled" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

<!-- Badges -->

[hacs-badge]: https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square
[release-badge]: https://img.shields.io/github/v/release/MelleD/ha-radar-warning?style=flat-square
[downloads-badge]: https://img.shields.io/github/downloads/MelleD/ha-radar-warning/total?style=flat-square
[build-badge]: https://img.shields.io/github/actions/workflow/status/MelleD/ha-radar-warning/build.yml?branch=main&style=flat-square
[paypal-me-badge]: https://img.shields.io/static/v1.svg?label=%20&message=PayPal.Me&logo=paypal
[buy-me-a-coffee-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white

<!-- References -->

[hacs-url]: https://github.com/hacs/integration
[home-assistant]: https://www.home-assistant.io/
[hacs]: https://hacs.xyz
[release-url]: https://github.com/MelleD/ha-radar-warning/releases
[paypal-me-url]: https://www.paypal.me/MelleDennis
[buy-me-a-coffee-url]: https://www.buymeacoffee.com/melled

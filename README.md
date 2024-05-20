# Discord Bouncer

A Discord Bot that leverages Stripe payments for role assignment.

## How it Works

1) Guild members react to a specific message to pay for 1 month of access to the Discord Role.

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/79dd7e33-a3fd-417f-9147-dfd78b716558)

2) Upon reacting, the bot sends a Direct Message (DM) to the member with a link for payment corresponding to their chosen Discord Role.

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/ebfceb95-2170-4654-a4e4-1bb04445b23e)

3) After the member completes the payment, a third-party website receives a 'checkout.session.completed' event from Stripe and sends a confirmation message to Discord that contains useful payment information data.

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/58f5f2ae-2c52-42c1-81d4-11088efc3f84) 

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/fe21b9b0-f381-40c2-ba01-6e51e9580849)

4) Finally, the Discord Bot assigns the paid role to the member in the Discord Guild.

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/f52eca27-a1c1-42d5-9b0a-25454a019e37)

## Technologies Utilized
The entire infrastructure of this Discord Bot is cloud-based, leveraging the complimentary tiers of Make.com and Google Cloud. This ensures continuous, cost-effective operation of the bot.

The specific tools employed include:
- Google e2-micro Compute Instance
- Google Firestore
- Google Secrets Manager
- Make.com Scenarios
- Docker
- Python + Poetry

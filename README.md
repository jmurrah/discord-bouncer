# Discord Bouncer

A Discord Bot that leverages Stripe payments for role assignment.

## How it Works

1) Guild members react to a specific message to choose their preferred payment method.

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/ddf770e8-6910-4195-8c32-c57acb963712)

2) Upon selection, the bot sends a Direct Message (DM) to the member with a link for payment corresponding to their chosen Discord Role.

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/7bdafc61-02ce-4bda-a8d3-454d51d56010)

3) After the member completes the payment, a third-party website receives a 'checkout.session.completed' event from Stripe and sends a confirmation message to Discord that contains useful payment information data.

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/e9996eed-93ee-4e36-9574-2d08be1b46aa) ![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/d41109c6-8ab1-4052-bd70-e4f60fb02399)

4) Finally, the Discord Bot assigns the paid role to the member in the Discord Guild.

![image](https://github.com/jmurrah/discord-bouncer/assets/110310485/9edd549b-12ac-49e1-8ad7-d86bd7085b11)

## Technologies Utilized
The entire infrastructure of this Discord Bot is cloud-based, leveraging the complimentary tiers of Make.com and Google Cloud. This ensures continuous, cost-effective operation of the bot.

The specific tools employed include:
- Google e2-micro Compute Instance
- Google Firestore
- Google Secrets Manager
- Make.com Scenarios
- Docker
- Python + Poetry

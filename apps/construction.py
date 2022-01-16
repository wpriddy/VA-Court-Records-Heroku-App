from dash import html


layout = html.Div([
    
    html.H1("Site is Currently Under Construction", style = {'textAlign': 'center'}),
        html.H3("Check Back Later To See The Latest Updates", style = {'textAlign': 'center'}),
    html.Img(src='https://images.squarespace-cdn.com/content/v1/5bdb27ee9772ae1cc7955a0a/1551380747835-EI2FP4GB8PCIESBV0AH7/UnderConstruction.png?format=1500w',
        className='construction')
])

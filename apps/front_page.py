from dash import html

layout = html.Div([

    html.H1("Virginia Court Records Analysis", 
    
        style = {
                'textAlign': 'center',
                'color': '#2C2C2C',
                'font-weight': 'bold',
                'margin-top': '20px'             
            }),

    html.P(
        children = [
        html.Spacer(),
        html.Br(),
        'The analysis of the Virginia Court Records was conceived as a project to inform the general public about trends in demographics across the state to supplement the open source ',
        html.A('Virginia Online Case Information System 2.0.', href = 'https://eapps.courts.state.va.us/ocis/landing'),
        html.Br(),
        html.Br(),
        'A special thank you to Ben Schoenfeld, who provided the open source data at ',
        html.A('https://virginiacourtdata.org.', href= 'https://virginiacourtdata.org/'),
        ' You can view the source code on his GitHub account ',
        html.A('https://github.com/bschoenfeld.', href='https://github.com/bschoenfeld'),
        html.Br(),
        html.Br(),
        'This analysis is brought to you by ',
        html.A('Wyatt Priddy', href='https://github.com/wpriddy'),
        ' and ',
        html.A('Dr. John Matter.', href = 'https://github.com/johnmatter'),
        html.Br(), html.Br(),
        'For thoughts on additional analysis or interest in collaboration, please reach out to Wyatt Priddy at wyattpriddy50@gmail.com.'
        ] + [html.Br() for _ in range(15)],
        
        
        ),

    ]

)

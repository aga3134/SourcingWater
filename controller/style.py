
def BasinStyle(lineColor="#fff",lineWidth=1,fill=False,fillColor="#f33"):
    lineStyle = {
        "type":"line",
        "paint": {
            "line-color":lineColor,
            "line-width":lineWidth
        },
    }
    fillStyle = {
        "type":"fill",
        "paint":{
            "fill-color":fillColor,
            "fill-opacity":[
                "case",
                ["boolean", ["feature-state", "hover"], False],
                0.5, 0
            ]
        }
    }
    style = [lineStyle]
    if fill:
        style.append(fillStyle)
    return style

def SymbolStyle(iconName, textKey = "name", allowOverlap = False, selectedTextColor="#f33"):
    return [
        {
            "type": "symbol",
            "layout":{
                "icon-image": iconName,
                "text-field": ["get", textKey],
                "text-size": 12,
                "text-offset": [0, 1.25],
                "text-anchor": "top",
                "icon-allow-overlap": allowOverlap,
                "text-allow-overlap": allowOverlap
            },
            "paint":{
                "text-color": [
                    'case',
                    ['boolean', ['feature-state', 'selected'], False], "#ff3",
                    "#fff"
                ],
                "text-halo-color": "#000",
                "text-halo-width":1,
                "text-halo-blur": 3
            }
        }
    ]

def CircleStyle():
    return [
        {
            "type": "line",
            "paint": {
                "line-color": "#f33",
                "line-width": 2
            }
        }
    ]

def FlowPathStyle(lineWidth=1,color="#fff",colorKey=None):
    lineStyle = {
        "type": "line",
        "paint":{
            "line-color": color,
            "line-width": lineWidth
        }
    }
    if colorKey is not None:
        lineStyle["paint"]["line-color"] = ["get",colorKey]
    return [lineStyle]

def SubbasinStyle(fillKey=None):
    lineStyle = {
        "type": "line",
        "paint":{
            "line-color": [
                'case',
                ['boolean', ['feature-state', 'selected'], False], "#ff3",
                "#fff"
            ],
            "line-width": [
                'case',
                ['boolean', ['feature-state', 'selected'], False], 2,
                1
            ],
        }
    }
    fillStyle = {
        "type": "fill",
        "paint":{
            "fill-color": "#33f",
            "fill-opacity": 0.5
        }
    }
    if fillKey is not None:
        fillStyle["paint"]["fill-color"] = ["get",fillKey]
    return [fillStyle,lineStyle]

def LivingAreaStyle(lineWidth=4,lineColor="#ff3",fill=False):
    lineStyle = {
        "type": "line",
        "paint": {
            "line-color": lineColor,
            "line-width": lineWidth
        }
    }
    fillStyle = {
        "type": "fill",
        "paint": {
            "fill-color": [
                'case',
                ['boolean', ['feature-state', 'selected'], False], "#ff3",
                ['boolean', ['feature-state', 'hover'], False], "#f93",
                "#fff"
            ],
            "fill-opacity": 0.5
        }
    }
    style = []
    if fill:
        style.append(fillStyle)
    style.append(lineStyle)
    return style

def AgricultureAreaStyle():
    return [{
        "type": "line",
        "paint": {
            "line-color": "#3f3",
            "line-width": 4
        }
    }]

def IndustryAreaStyle():
    return [
        {
            "type": "fill",
            "paint": {
                "fill-color": "#33f",
                "fill-opacity": 0.5
            }
        },
        {
            "type": "line",
            "paint": {
                "line-color": [
                    'case',
                    ['boolean', ['feature-state', 'selected'], False], "#ff3",
                    ['boolean', ['feature-state', 'hover'], False], "#f93",
                    "#fff"
                ],
                "line-width": 2
            }
        }
    ]

def StatisticAreaStyle():
    return [{
        "type": "line",
        "paint": {
            "line-color": "#f3f",
            "line-width": 2
        }
    }]

def FloodStyle(fillKey=None):
    lineStyle = {
        "type": "line",
        "paint":{
            "line-color": "#fff",
            "line-width": 1
        }
    }
    fillStyle = {
        "type": "fill",
        "paint":{
            "fill-color": "#33f",
            "fill-opacity": 0.5
        }
    }
    if fillKey is not None:
        fillStyle["paint"]["fill-color"] = ["get",fillKey]
    return [fillStyle,lineStyle]
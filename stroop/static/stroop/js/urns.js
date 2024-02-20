// const HIGHLIGHT_COLORS = ["#4472c4", "#ed7d31", "#009B72"]; // "#FF0F80"
    const HIGHLIGHT_COLORS = ["#547FC9", "#FF0A7C", "#00CC96"]; // "#ed7d31"
function get_fill_color(ball, cutoffs, colors) {
    // console.log(ball, cutoffs);
    for (let i = 0; i < cutoffs.length; i++) {
        if (ball <= cutoffs[i]) {
            return colors[i];
        }
    }
    return colors[colors.length - 1]
}

function draw_urn(element_name, radius, highlight_shares) {
    let NS = "http://www.w3.org/2000/svg";
    let svg = document.getElementById(element_name);
    // 10 * 2 * radius + 10 * 0.5 * radius + 0.5 radius
    // we set the distance between circles to be half their radius
    // we add 1/2 distance on either side to the urn sides
    let size = 25.5 * radius;
    let line_min = 0.5;
    let line_max = size - 0.5;

    svg.setAttribute("width", size);
    svg.setAttribute("height", size);
    
    // urn box
    // the minimum stroke width is set to 1
    // it otherwise scales with the radius (1/4 radius)
    let stroke_width = Math.floor(radius / (2 * 2));
    if (stroke_width < 1) {
        stroke_width = 1;
    }
    let box = document.createElementNS(NS, "polyline");
    box.setAttribute("points", `${line_min},${line_min} ${line_min},${line_max} ${line_max},${line_max} ${line_max},${line_min}`);
    box.setAttribute("style", `fill: none; stroke: black; stroke-width: ${stroke_width}`);
    svg.appendChild(box);
    
    
    
    // determine nuber of highlighted balls
    let highlight_balls = make_cutoffs(highlight_shares);
    
    //console.log(highlight_balls);
    
    let x_pos, y_pos;
    let ball_counter = 0;
    let fill_color;
    for (let row = 1; row <= 10; row++) {
        y_pos = row * radius / 2 + (2 * row - 1) * radius
        for (let col = 1; col <= 10; col++) {
            ball_counter++;
            let circle = document.createElementNS(NS, "circle");
            x_pos = col * radius / 2 + (2 * col - 1) * radius;
            circle.setAttribute("r", radius)
            circle.setAttribute("cx", x_pos);
            circle.setAttribute("cy", y_pos);
            fill_color = get_fill_color(ball_counter, highlight_balls, HIGHLIGHT_COLORS);
            circle.setAttribute("fill", fill_color);
            svg.appendChild(circle);
            
        }
    }
}

function make_cutoffs(shares) {
    let cutoffs = [];
    for (let i = 0; i < shares.length; i++) {
        let base = i === 0 ? 0 : cutoffs[i-1];
        cutoffs.push(base + Math.round(shares[i] * 100));
    }
    return cutoffs
}
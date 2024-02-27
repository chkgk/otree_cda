let purchase_history_body = document.getElementById("id_purchase_history");
let sale_history_body = document.getElementById("id_sales_history");

let ask_table_body = document.getElementById("id_ask_orders");
let bid_table_body = document.getElementById("id_bid_orders");

let ask_limit_quantity = document.getElementById("id_ask_limit_quantity");
let ask_limit_price = document.getElementById("id_ask_limit_price");

let bid_limit_quantity = document.getElementById("id_bid_limit_quantity");
let bid_limit_price = document.getElementById("id_bid_limit_price");

let place_limit_ask = document.getElementById("id_place_limit_ask");
let place_limit_bid = document.getElementById("id_place_limit_bid");

// market
let ask_market_quantity = document.getElementById("id_ask_market_quantity");
let bid_market_quantity = document.getElementById("id_bid_market_quantity");

let place_market_ask = document.getElementById("id_place_market_ask");
let place_market_bid = document.getElementById("id_place_market_bid");

let ask_orders = [];
let bid_orders = [];

let purchase_history = [];
let sale_history = [];

let cash_field = document.getElementById("id_cash");
let assets_field = document.getElementById("id_assets");
let available_cash_field = document.getElementById("id_available_cash");
let available_assets_field = document.getElementById("id_available_assets");
let stock_price_field = document.getElementById("id_stock_price");

let cash, assets, last_price, available_assets, available_cash;
let market_start = js_vars.market_start;

let my_player_id = js_vars.player_id;

function is_empty(obj) {
    return Object.keys(obj).length === 0;
}
function setup() {
    ask_orders = js_vars.asks;
    bid_orders = js_vars.bids;
    purchase_history = js_vars.purchase_history;
    sale_history = js_vars.sale_history;
    cash = js_vars.cash;
    assets = js_vars.assets;
    available_assets = js_vars.available_assets;
    available_cash = js_vars.available_cash;
    last_price = js_vars.last_price;
    stock_price_field.innerHTML = last_price || "";
    available_cash_field.innerHTML = available_cash;
    available_assets_field.innerHTML = available_assets;
    price_chart.series[0].setData(js_vars.chart_series);
    draw_table(ask_table_body, ask_orders);
    draw_table(bid_table_body, bid_orders);
    draw_history_table(purchase_history_body, purchase_history);
    draw_history_table(sale_history_body, sale_history);
}

function liveRecv(data) {
    console.log(data);
    if (data.type === "order") {
        handle_order(data.payload);
    }
    
    if (data.type === "order_cancelled") {
        remove_order(data.payload.order_data.uuid);
    }
    
    if (data.type === "market_order_filled") {
        remove_order(data.payload.to_remove);
        if (data.payload.to_add) {
            if (data.payload.to_add.side === "ask") {
                add_ask_order(ask_orders, data.payload.to_add)
                draw_table(ask_table_body, ask_orders);
            }
            if (data.payload.to_add.side === "bid") {
                add_bid_order(bid_orders, data.payload.to_add)
                draw_table(bid_table_body, bid_orders);
            }
        }
        stock_price_field.innerHTML = data.payload.last_price;
        let current_second = Math.floor(Date.now() / 1000) - market_start;
        price_chart.series[0].addPoint([current_second, data.payload.last_price]);
    }
    update_if_affected(data.payload.affected_players);
}

function handle_order(payload) {
    if (payload.order_data.kind === "limit") {
        if (payload.order_data.side === "ask") {
            ask_placed(payload.order_data)
        }
        if (payload.order_data.side === "bid") {
            bid_placed(payload.order_data)
        }
    }
}

function update_if_affected(data) {
    if (data.hasOwnProperty(my_player_id)) {
        cash = data[my_player_id].cash;
        assets = data[my_player_id].assets;
        available_cash = data[my_player_id].available_cash;
        available_assets = data[my_player_id].available_assets;
        cash_field.innerHTML = cash;
        assets_field.innerHTML = assets;
        available_cash_field.innerHTML = available_cash;
        available_assets_field.innerHTML = available_assets;
        
        if (!is_empty(data[my_player_id].purchase_history_add)) {
            purchase_history.unshift(data[my_player_id].purchase_history_add);
            draw_history_table(purchase_history_body, purchase_history);
        }
        if (!is_empty(data[my_player_id].sale_history_add)) {
            sale_history.unshift(data[my_player_id].sale_history_add);
            draw_history_table(sale_history_body, sale_history);
        }
    }
}

function remove_order(uuid) {
    for (let i = 0; i < bid_orders.length; i++) {
        if (bid_orders[i].uuid === uuid) {
            bid_orders.splice(i, 1);
            draw_table(bid_table_body, bid_orders);
            break;
        }
    }
    for (let i = 0; i < ask_orders.length; i++) {
        if (ask_orders[i].uuid === uuid) {
            ask_orders.splice(i, 1);
            draw_table(ask_table_body, ask_orders);
            break;
        }
    }
}

function add_table_row(table, data) {
    let row = document.createElement("tr");
    let price = document.createElement("td");
    let quantity = document.createElement("td");
    price.innerHTML = data.price;
    quantity.innerHTML = data.quantity;
    
    row.appendChild(price);
    row.appendChild(quantity);
    
    let action = document.createElement("td");
    if (data.player_id === my_player_id) {
        let del_link = document.createElement("a");
        del_link.addEventListener('click', function() {
            liveSend({'type': 'cancel_order', 'payload': {'uuid': data.uuid}});
        });
        del_link.href = "#";
        del_link.innerHTML = "<i class=\"bi bi-trash\"></i>";
        action.appendChild(del_link);
    } else {
        action.innerHTML = "&nbsp;";
    }
    row.appendChild(action);
    table.appendChild(row);
}
function add_history_table_row(table, data) {
    let row = document.createElement("tr");
    let price = document.createElement("td");
    let quantity = document.createElement("td");
    price.innerHTML = data.price;
    quantity.innerHTML = data.quantity;
    
    row.appendChild(price);
    row.appendChild(quantity);
    
    table.appendChild(row);
}

function draw_table(table, data) {
    table.innerHTML = "";
    for (let i = 0; i < data.length; i++) {
        add_table_row(table, data[i]);
    }
}

function draw_history_table(table, data) {
    table.innerHTML = "";
    for (let i = 0; i < data.length; i++) {
        add_history_table_row(table, data[i]);
    }
}

function ab_price(a, b) {
    return a.price - b.price;
}

function ba_price(a, b) {
    return b.price - a.price;
}

function add_ask_order(order_list, data) {
    order_list.push(data)
    order_list.sort(ab_price);
}
function add_bid_order(order_list, data) {
    order_list.push(data)
    order_list.sort(ba_price);
}

function ask_placed(data) {
    add_ask_order(ask_orders, data)
    draw_table(ask_table_body, ask_orders);
}

function bid_placed(data) {
    add_bid_order(bid_orders, data)
    draw_table(bid_table_body, bid_orders);
}

function place_order(type, quantity, price) {
    if (quantity === "" || isNaN(quantity)){
        console.log("quantity is always required")
        return;
    }
    if (quantity <= 0) {
        console.log("quantity must be positive")
        return;
    }
    
    if (type === "place_limit_bid") {
        if (price === "") {
            console.log("price is required for limit orders")
            return;
        }
        if (price <= 0) {
            console.log("price must be positive")
            return;
        }
        if (quantity * price > available_cash) {
            console.log("not enough cash")
            return;
        }
        if (ask_orders.length > 0 && price >= parseInt(ask_orders[0].price)) {
            console.log("price too high")
            return;
        }
        liveSend({'type': 'order', 'payload': {'kind': 'limit', 'side': 'bid', 'quantity': quantity, 'price': price}});
    }
    
    if (type === "place_limit_ask") {
        if (price === "") {
            console.log("price is required for limit orders")
            return;
        }
        if (price <= 0) {
            console.log("price must be positive")
            return;
        }
        if (price * quantity > available_cash) {
            console.log("not enough cash")
            return;
        }
        if (bid_orders.length > 0 && price <= parseInt(bid_orders[0].price)) {
            console.log("price too low")
            return;
        }
        liveSend({'type': 'order', 'payload': {'kind': 'limit', 'side': 'ask', 'quantity': quantity, 'price': price}});
    }
    
    if (type === "place_market_ask") {
        if (bid_orders[0].player_id === my_player_id) {
            console.log("cannot sell to self")
            return;
        }
        if (quantity > available_assets) {
            console.log("not enough assets")
            return;
        }
        liveSend({'type': 'order', 'payload': {'kind': 'market', 'side': 'ask', 'quantity': quantity}});
    }
    
    if (type === "place_market_bid") {
        if (ask_orders[0].player_id === my_player_id) {
            console.log("cannot buy from self")
            return;
        }
        if (quantity * parseInt(ask_orders[0].price) > available_cash) {
            console.log("not enough cash")
            return;
        }
        liveSend({'type': 'order', 'payload': {'kind': 'market', 'side': 'bid', 'quantity': quantity}});
    }
}

// handle placing asks and bids
function place_limit_ask_handler() {
    let price = parseInt(ask_limit_price.value);
    let quantity = parseInt(ask_limit_quantity.value);
    place_order('place_limit_ask', quantity, price);
    ask_table_body.scrollTop = 0;
    ask_limit_price.value = "";
    ask_limit_quantity.value = "";
    ask_limit_quantity.focus();
}

function place_limit_bid_handler() {
    let price = parseInt(bid_limit_price.value);
    let quantity = parseInt(bid_limit_quantity.value);
    place_order('place_limit_bid', quantity, price);
    bid_table_body.scrollTop = 0;
    bid_limit_price.value = "";
    bid_limit_quantity.value = "";
    bid_limit_quantity.focus();
}

function place_market_ask_handler() {
    let quantity = parseInt(ask_market_quantity.value);
    place_order('place_market_ask', quantity);
    bid_table_body.scrollTop = 0;
    ask_market_quantity.value = "";
    ask_market_quantity.focus();
}

function place_market_bid_handler() {
    let quantity = parseInt(bid_market_quantity.value);
    place_order('place_market_bid', quantity);
    ask_table_body.scrollTop = 0;
    bid_market_quantity.value = "";
    bid_market_quantity.focus();
}

// input field enter key events
ask_limit_price.addEventListener('keyup', function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        place_limit_ask_handler()
    }
});
bid_limit_price.addEventListener('keyup', function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        place_limit_bid_handler()
    }
});

ask_market_quantity.addEventListener('keyup', function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        place_market_ask_handler()
    }
});

bid_market_quantity.addEventListener('keyup', function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        place_market_bid_handler()
    }
});

// button click events
place_limit_ask.addEventListener('click', function() {
    place_limit_ask_handler()
});

place_limit_bid.addEventListener('click', function() {
    place_limit_bid_handler()
});

place_market_ask.addEventListener('click', function() {
    place_market_ask_handler()
});

place_market_bid.addEventListener('click', function() {
    place_market_bid_handler()
});

setup()

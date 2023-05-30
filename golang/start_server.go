package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

type Closed_order struct {
	Open_time   string  `json:"open_time"`
	Close_time  string  `json:"close_time"`
	Entry_price float64 `json:"entry_price"`
	Profit      float64 `json:"profit"`
}
type Open_order struct {
	Open_time   string  `json:"open_time"`
	Entry_price float64 `json:"entry_price"`
}

type Alerts struct {
	ID            int     `json:"id"`
	Creation_time string  `json:"creation_time"`
	Direction     string  `json:"direction"`
	Trigger_price float64 `json:"trigger_price"`
}

type PercAlerts struct {
	ID             int     `json:"id"`
	Creation_time  string  `json:"creation_time"`
	Symbol         string  `json:"symbol"`
	Perc           float64 `json:"perc"`
	Direction      string  `json:"direction"`
	Last_trig_time *string `json:"last_trig_time"`
}

type WhaleAlerts struct {
	ID            int     `json:"id"`
	Creation_time string  `json:"creation_time"`
	Order_type    string  `json:"order_type"`
	Symbol        string  `json:"symbol"`
	Amount        float64 `json:"amount"`
	Group_size    float64 `json:"group_size"`
}

type Bot_settings struct {
	Stop        float64 `json:"stop"`
	P_stop1_t   float64 `json:"p_stop1_t"`
	P_stop1     float64 `json:"p_stop1"`
	P_stop2_t   float64 `json:"p_stop2_t"`
	P_stop2     float64 `json:"p_stop2"`
	P_stop3_t   float64 `json:"p_stop3_t"`
	P_stop3     float64 `json:"p_stop3"`
	P_stop4_t   float64 `json:"p_stop4_t"`
	P_stop4     float64 `json:"p_stop4"`
	Take_profit float64 `json:"take_profit"`
}

type M map[string]interface{}

func getRoot(w http.ResponseWriter, r *http.Request) {
	var a []Closed_order
	var b []Open_order
	db, err := sql.Open("mysql", "$USER:$PASS@tcp($SQL_SERVER_ADDRESS:3306)/ORDERS")

	if err != nil {
		panic(err.Error())
	}

	defer db.Close()

	//date, error := time.Parse("02/01/2006 15:04:05", r.FormValue("start_date"))

	//fmt.Printf("%s", date)
	/*
		if error != nil {
			fmt.Println(error)
			panic(error.Error())

		}
	*/

	//results, err := db.Query("SELECT open_time, close_time, entry_price, profit FROM closed_orders")

	var query string

	if r.FormValue("start_date") != "" && r.FormValue("end_date") != "" {

		query = fmt.Sprintf("SELECT open_time, close_time, entry_price, profit FROM closed_orders where STR_TO_DATE(open_time, '%%d/%%m/%%Y') BETWEEN '%s' and '%s'", r.FormValue("start_date"), r.FormValue("end_date"))

	} else {
		query = "SELECT open_time, close_time, entry_price, profit FROM closed_orders"
	}
	results, err := db.Query(query)

	if err != nil {
		panic(err.Error())
	}

	for results.Next() {
		var closed_order Closed_order
		err = results.Scan(&closed_order.Open_time, &closed_order.Close_time, &closed_order.Entry_price, &closed_order.Profit)
		if err != nil {
			panic(err.Error())
		}

		a = append(a, closed_order)

	}

	results2, err1 := db.Query("SELECT open_time, entry_price FROM open_orders")
	if err1 != nil {
		panic(err.Error()) // proper error handling instead of panic in your app
	}

	for results2.Next() {
		var open_order Open_order
		// for each row, scan the result into our tag composite object
		err1 = results2.Scan(&open_order.Open_time, &open_order.Entry_price)

		if err1 != nil {
			panic(err1.Error()) // proper error handling instead of panic in your app
		}

		b = append(b, open_order)

	}

	var sum_profit float64
	sum_profit = 0.0
	for _, element := range a {

		sum_profit += element.Profit

	}

	t, _ := template.ParseFiles("home.html")

	err2 := t.Execute(w, M{
		"Closed":      a,
		"Open":        b,
		"TotalProfit": sum_profit,
	})
	if err2 != nil {
		fmt.Println("executing template:", err2)
	}

}

func select_bot_settings(mdb *sql.DB) []Bot_settings {

	var bot_set_l []Bot_settings

	results, err := mdb.Query("SELECT stop, p_stop1_t, p_stop1, p_stop2_t, p_stop2, p_stop3_t, p_stop3, p_stop4_t, p_stop4, take_profit FROM Bot_settings")
	if err != nil {
		panic(err.Error()) // proper error handling instead of panic in your app
	}

	for results.Next() {
		var bot_set Bot_settings
		// for each row, scan the result into our tag composite object
		err = results.Scan(&bot_set.Stop, &bot_set.P_stop1_t, &bot_set.P_stop1, &bot_set.P_stop2_t, &bot_set.P_stop2, &bot_set.P_stop3_t, &bot_set.P_stop3, &bot_set.P_stop4_t, &bot_set.P_stop4, &bot_set.Take_profit)
		if err != nil {
			panic(err.Error()) // proper error handling instead of panic in your app
		}

		bot_set_l = append(bot_set_l, bot_set)

	}
	return bot_set_l
}

func select_alerts(mdb *sql.DB) []Alerts {

	var alert_l []Alerts

	results, err := mdb.Query("SELECT Alertid, Creation_time, Direction, Trigger_Price FROM Alerts")
	if err != nil {
		panic(err.Error()) // proper error handling instead of panic in your app
	}

	for results.Next() {
		var alert Alerts
		// for each row, scan the result into our tag composite object
		err = results.Scan(&alert.ID, &alert.Creation_time, &alert.Direction, &alert.Trigger_price)
		if err != nil {
			panic(err.Error()) // proper error handling instead of panic in your app
		}

		alert_l = append(alert_l, alert)

	}
	return alert_l
}

func perc_select_alerts(mdb *sql.DB) []PercAlerts {

	var alert_l []PercAlerts

	results, err := mdb.Query("SELECT id, creation_time, symbol, perc, direction, last_trig_time FROM PercAlert")
	if err != nil {
		panic(err.Error()) // proper error handling instead of panic in your app
	}

	for results.Next() {
		var alert PercAlerts
		// for each row, scan the result into our tag composite object
		err = results.Scan(&alert.ID, &alert.Creation_time, &alert.Symbol, &alert.Perc, &alert.Direction, &alert.Last_trig_time)
		if err != nil {
			panic(err.Error()) // proper error handling instead of panic in your app
		}

		alert_l = append(alert_l, alert)

	}
	return alert_l
}

func whale_select_alerts(mdb *sql.DB) []WhaleAlerts {

	var alert_l []WhaleAlerts

	results, err := mdb.Query("SELECT id, creation_time, order_type, symbol, amount, group_size FROM WhaleAlert")
	if err != nil {
		panic(err.Error()) // proper error handling instead of panic in your app
	}

	for results.Next() {
		var alert WhaleAlerts
		// for each row, scan the result into our tag composite object
		err = results.Scan(&alert.ID, &alert.Creation_time, &alert.Order_type, &alert.Symbol, &alert.Amount, &alert.Group_size)
		if err != nil {
			panic(err.Error()) // proper error handling instead of panic in your app
		}

		alert_l = append(alert_l, alert)

	}
	return alert_l
}

func getAlerts(w http.ResponseWriter, r *http.Request) {

	db, err := sql.Open("mysql", "$USER:$PASS@tcp($SQL_SERVER_ADDRESS:3306)/ORDERS")

	if err != nil {
		panic(err.Error())
	}

	defer db.Close()

	switch r.Method {
	case "GET":

		t, _ := template.ParseFiles("alerts.html")

		err := t.Execute(w, M{
			"Alert":       select_alerts(db),
			"Perc_alert":  perc_select_alerts(db),
			"Whale_alert": whale_select_alerts(db),
		})
		if err != nil {
			fmt.Println("executing template:", err)
		}

	case "POST":
		if err := r.ParseForm(); err != nil {
			//fmt.Fprintf(w, "ParseForm() err: %v", err)
			return
		}

		price := r.FormValue("trig_price")
		if price != "" {

			query := fmt.Sprintf("INSERT INTO Alerts (Creation_time, Direction, Trigger_Price) VALUES ('%s', '%s' ,%s)", time.Now().Format("02/01/2006 15:04:05"), r.FormValue("direction"), r.FormValue("trig_price"))

			_, err1 := db.Query(query)

			if err1 != nil {
				panic(err.Error()) // proper error handling instead of panic in your app
			}

		} else if r.FormValue("delete") != "" {
			query := fmt.Sprintf("DELETE FROM Alerts WHERE Alertid = %s ", r.FormValue("delete"))

			_, err1 := db.Query(query)

			if err1 != nil {
				panic(err.Error()) // proper error handling instead of panic in your app
			}
		} else if r.FormValue("perc") != "" {

			query := fmt.Sprintf("INSERT INTO PercAlert (creation_time, symbol, perc, direction) VALUES ('%s', '%s', %s, '%s')", time.Now().Format("02/01/2006 15:04:05"), r.FormValue("symbol"), r.FormValue("perc"), r.FormValue("direction_perc"))

			_, err1 := db.Query(query)

			if err1 != nil {
				panic(err.Error()) // proper error handling instead of panic in your app
			}

		} else if r.FormValue("delete_perc") != "" {
			query := fmt.Sprintf("DELETE FROM PercAlert WHERE id = %s ", r.FormValue("delete_perc"))

			_, err1 := db.Query(query)

			if err1 != nil {
				panic(err.Error()) // proper error handling instead of panic in your app
			}
		} else if r.FormValue("whale_amount") != "" {

			query := fmt.Sprintf("INSERT INTO WhaleAlert (creation_time, order_type, symbol, amount, group_size) VALUES ('%s', '%s', '%s', %s, %s)", time.Now().Format("02/01/2006 15:04:05"), r.FormValue("whale_order_type"), r.FormValue("symbol_whale"), r.FormValue("whale_amount"), r.FormValue("whale_group_size"))

			_, err1 := db.Query(query)

			if err1 != nil {
				panic(err.Error()) // proper error handling instead of panic in your app
			}

		} else {
			query := fmt.Sprintf("DELETE FROM WhaleAlert WHERE id = %s ", r.FormValue("delete_whale"))

			_, err1 := db.Query(query)

			if err1 != nil {
				panic(err.Error()) // proper error handling instead of panic in your app
			}
		}

		t, _ := template.ParseFiles("alerts.html")

		err2 := t.Execute(w, M{
			"Alert":       select_alerts(db),
			"Perc_alert":  perc_select_alerts(db),
			"Whale_alert": whale_select_alerts(db),
		})
		if err2 != nil {
			fmt.Println("executing template:", err2)
		}

	default:
		fmt.Fprintf(w, "Sorry, only GET and POST methods are supported.")
	}

}

func getSettings(w http.ResponseWriter, r *http.Request) {

	db, err := sql.Open("mysql", "$USER:$PASS@tcp($SQL_SERVER_ADDRESS:3306)/ORDERS")
	if err != nil {
		panic(err.Error())
	}

	defer db.Close()

	switch r.Method {
	case "GET":

		t, _ := template.ParseFiles("bot_settings.html")

		err := t.Execute(w, M{
			"Settings": select_bot_settings(db),
		})
		if err != nil {
			fmt.Println("executing template:", err)
		}

	case "POST":

		t, _ := template.ParseFiles("bot_settings.html")

		err3 := r.ParseForm()
		if err3 != nil {
			panic(err3.Error())
		}

		for key, value := range r.Form {

			if value[0] != "" {

				query := fmt.Sprintf("UPDATE Bot_settings SET %s = '%s' WHERE id = 1", key, value[0])

				_, err1 := db.Query(query)

				if err1 != nil {
					panic(err1.Error())
				}

			}

		}

		err2 := t.Execute(w, M{
			"Settings": select_bot_settings(db),
		})
		if err2 != nil {
			fmt.Println("executing template:", err2)
		}

	}

}

func main() {

	http.HandleFunc("/", getRoot)
	http.HandleFunc("/Alerts", getAlerts)
	http.HandleFunc("/BotSettings", getSettings)

	fs := http.FileServer(http.Dir("css"))

	http.Handle("/css/", http.StripPrefix("/css/", fs))

	fs2 := http.FileServer(http.Dir("images"))
	http.Handle("/images/", http.StripPrefix("/images/", fs2))

	log.Fatal(http.ListenAndServe(":80", nil))

}

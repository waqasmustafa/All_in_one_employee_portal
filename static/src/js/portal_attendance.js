/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PortalAttendance = publicWidget.Widget.extend({
    selector: '.o_employee_portal_dashboard',
    events: {
        'click #o_portal_attendance_toggle_btn': '_onToggleAttendance',
    },

    _onToggleAttendance: function (ev) {
        const btn = ev.currentTarget;
        const statusText = document.getElementById('o_portal_attendance_status');
        
        btn.disabled = true;
        btn.innerText = "Processing...";

        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this._submitAttendance(position.coords.latitude, position.coords.longitude, btn, statusText);
                },
                (error) => {
                    console.error("Geolocation error:", error);
                    this._submitAttendance(null, null, btn, statusText);
                },
                { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
            );
        } else {
            this._submitAttendance(null, null, btn, statusText);
        }
    },

    _submitAttendance: function (lat, long, btn, statusText) {
        // Use standard fetch to avoid Odoo dependency issues in portal
        fetch('/my/attendance/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                jsonrpc: "2.0",
                params: {
                    latitude: lat,
                    longitude: long,
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            const result = data.result;
            if (result && result.status) {
                if (result.status === 'checked_in') {
                    btn.innerText = "Check Out";
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-danger');
                    statusText.innerText = "Checked In";
                } else {
                    btn.innerText = "Check In";
                    btn.classList.remove('btn-danger');
                    btn.classList.add('btn-success');
                    statusText.innerText = "Checked Out";
                }
            } else if (result && result.error) {
                alert(result.error);
            }
        })
        .catch(err => {
            console.error("Attendance failed:", err);
            alert("Something went wrong. Please try again.");
        })
        .finally(() => {
            btn.disabled = false;
        });
    },
});

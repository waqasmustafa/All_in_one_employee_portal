/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const attendanceBtn = document.getElementById('o_portal_attendance_toggle_btn');
    const statusText = document.getElementById('o_portal_attendance_status');

    if (attendanceBtn) {
        attendanceBtn.addEventListener('click', async () => {
            attendanceBtn.disabled = true;
            attendanceBtn.innerText = "Processing...";

            // Get Geolocation
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    async (position) => {
                        const latitude = position.coords.latitude;
                        const longitude = position.coords.longitude;
                        await toggleAttendance(latitude, longitude);
                    },
                    async (error) => {
                        console.error("Geolocation error:", error);
                        // Still allow check-in even if location fails, but log it
                        await toggleAttendance(null, null);
                    },
                    { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
                );
            } else {
                // Geolocation not supported
                await toggleAttendance(null, null);
            }
        });
    }

    async function toggleAttendance(lat, long) {
        try {
            const result = await jsonrpc('/my/attendance/toggle', {
                latitude: lat,
                longitude: long,
            });

            if (result.error) {
                alert(result.error);
                location.reload();
                return;
            }

            // Update UI
            if (result.status === 'checked_in') {
                attendanceBtn.innerText = "Check Out";
                attendanceBtn.classList.remove('btn-success');
                attendanceBtn.classList.add('btn-danger');
                statusText.innerText = "Checked In";
            } else {
                attendanceBtn.innerText = "Check In";
                attendanceBtn.classList.remove('btn-danger');
                attendanceBtn.classList.add('btn-success');
                statusText.innerText = "Checked Out";
            }
        } catch (err) {
            console.error("Attendance toggle failed:", err);
            alert("Something went wrong. Please try again.");
        } finally {
            attendanceBtn.disabled = false;
        }
    }
});

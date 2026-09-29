# Mobile App Documentation

React Native with Expo (SDK 57) and Expo Router. One app serves all four field roles; the interface adapts to the role in the login token.

## Screens by role

| Screen | Resident | Guardian | Volunteer | Security |
|---|---|---|---|---|
| Login / Register | yes | yes | yes | yes |
| SOS button with category, message, GPS | yes | | | |
| Active incident list | | yes | yes | yes |
| Incident detail with chat | yes | yes | yes | yes |
| Accept & Respond | | yes | yes | yes |
| Mark Resolved | yes | if responder | if responder | if responder |
| My Alerts history | yes | | | |
| Emergency contacts (3 tiers) | yes | | | |
| Notification inbox | | yes | yes | yes |
| Availability toggle | | | yes | yes |
| Profile / sign out | yes | yes | yes | yes |

## Project structure
mobile/
app/
_layout.js Root stack, wraps AuthProvider
index.js Redirects to login or tabs
login.js, register.js
(tabs)/
_layout.js Role-based tab bar, registers push token
index.js SOS (residents) or incident list (responders)
alerts.js Resident alert history
contacts.js Emergency contacts by tier
notifications.js Responder inbox
profile.js Account and availability
incident/[id].js Incident detail, actions, chat (auto-refresh 8s)
src/
api.js Axios client, JWT header, token refresh, error text
auth.js Auth context, SecureStore persistence
device.js Location capture, push registration
theme.js, ui.js Colours and shared components
app.json, eas.json

## Key behaviour

- **Tokens** are stored with `expo-secure-store` (Android Keystore), never plain storage
- **Expired access tokens** are refreshed automatically once, then the user is signed out
- **Location** is requested only when sending an SOS; the alert still sends if permission is denied
- **SOS confirmation dialog** prevents accidental triggers
- **Incident detail polls every 8 seconds** so chat and status stay current

## Configuration

The API address is one constant in `src/api.js`:

```js
export const BASE_URL = "https://community-emergency-response-platform.onrender.com";
```

For local development point it at your laptop's LAN IP, e.g. `http://192.168.x.x:8000`, and run Django with `python manage.py runserver 0.0.0.0:8000`.

## Running in development

```powershell
cd mobile
npm install
npx expo start --clear
```

Scan the QR code with Expo Go. Note: Expo Go on Android does not support remote push notifications since SDK 53; the app skips push registration there automatically.

## Building the Android APK

```powershell
cd mobile
npx eas-cli@latest login
npx eas-cli@latest build --platform android --profile preview
```

The `preview` profile produces an installable `.apk`. The build page on expo.dev provides a download link and QR code.

## Permissions

| Permission | Why |
|---|---|
| Location (while in use) | Attach GPS coordinates to an SOS |
| Notifications | Receive emergency alerts |

## Known limitations

- Device push on the APK additionally requires Firebase Cloud Messaging credentials in EAS; without them the app still works and alerts arrive through the in-app inbox, SMS, and email
- The free API host sleeps when idle; the first request after a long pause can take up to a minute
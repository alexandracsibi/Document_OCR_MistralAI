# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## Get started

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the app

   ```bash
   npx expo start
   ```

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Project skeleton

<pre>
.
├─ app/
│  ├─ (app)/
│  │  ├─ _layout.tsx         // authenticated app stack layout
│  │  ├─ home.tsx            // landing/home screen after login
│  │  ├─ capture.tsx         // take/select photo + choose doc_type + upload
│  │  └─ result.tsx          // show extracted fields + status/errors
│  ├─ (auth)/
│  │  ├─ _layout.tsx         // auth stack layout
│  │  └─ login.tsx           // Auth0 login entry
│  ├─ (lock)/
│  │  ├─ _layout.tsx         // lock stack layout
│  │  └─ unlock.tsx          // biometric/PIN gate before entering (app)
│  ├─ callback.tsx           // Auth0 redirect handler (PKCE/code exchange)
│  └─ index.tsx              // route entry: decide auth/lock/app redirect
└─ src/
   ├─ api/
   │  ├─ client.ts           // fetch wrapper, base URL, auth header injection
   │  └─ endpoints.ts        // typed functions: uploadPhoto(), etc.
   ├─ auth/
   │  ├─ auth0.ts            // Auth0 client config + login/logout
   │  ├─ session.ts          // token storage + refresh logic (later)
   │  ├─ biometric.ts        // local-authentication helper
   │  └─ pkce.ts             // PKCE helpers (code verifier/challenge)
   ├─ storage/
   │  └─ secureStore.ts      // wrapper around expo-secure-store
   ├─ config/
   │  └─ env.ts              // config from app.json extra / env vars
   └─ types/
      └─ api.ts              // API request/response types

</pre>
import Constants from "expo-constants";

type Extra = {
  AUTH0_DOMAIN?: string;
  AUTH0_CLIENT_ID?: string;
  AUTH0_AUDIENCE?: string;
  API_BASE_URL?: string;
};

const extra = (Constants.expoConfig?.extra ?? {}) as Extra;

export const ENV = {
  auth0Domain: (extra.AUTH0_DOMAIN ?? "").trim(),
  auth0ClientId: (extra.AUTH0_CLIENT_ID ?? "").trim(),
  auth0Audience: (extra.AUTH0_AUDIENCE ?? "").trim(), // optional
  apiBaseUrl: (extra.API_BASE_URL ?? "").trim(),      // optional for now
};

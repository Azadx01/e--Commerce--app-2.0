export type AuthStackParamList = {
    Splash: undefined;
    Login: undefined;
    Register: undefined;
};

export type HomeStackParamList = {
    Home: undefined;
    Devices: undefined;
    AddDevice: undefined;
    EditDevice: { deviceId: number };
    Profile: undefined;
};

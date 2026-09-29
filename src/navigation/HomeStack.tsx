import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { HomeStackParamList } from './types';
import { Home } from '../screens/Home';
import { Devices } from '../screens/Devices';
import { AddDevice } from '../screens/AddDevice';
import { EditDevice } from '../screens/EditDevice';
import { Profile } from '../screens/Profile';

const Stack = createNativeStackNavigator<HomeStackParamList>();

export const HomeStack = () => {
    return (
        <Stack.Navigator screenOptions={{ headerShown: false }} initialRouteName="Home">
            <Stack.Screen name="Home" component={Home} />
            <Stack.Screen name="Devices" component={Devices} />
            <Stack.Screen name="AddDevice" component={AddDevice} />
            <Stack.Screen name="EditDevice" component={EditDevice} />
            <Stack.Screen name="Profile" component={Profile} />
        </Stack.Navigator>
    );
};

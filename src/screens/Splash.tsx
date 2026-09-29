import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../navigation/types';
import { theme } from '../theme/theme';

type Props = {
    navigation: NativeStackNavigationProp<AuthStackParamList, 'Splash'>;
};

export const Splash = ({ navigation }: Props) => {
    useEffect(() => {
        // Simulated UI delay matching requirement to separate mock state from real API
        setTimeout(() => {
            navigation.replace('Login');
        }, 1500);
    }, [navigation]);

    return (
        <View style={styles.container}>
            <Text style={styles.logo}>ReVivo</Text>
            <Text style={styles.tagline}>Repair. Resell. Reuse.</Text>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: theme.colors.primary,
        justifyContent: 'center',
        alignItems: 'center',
    },
    logo: {
        ...theme.typography.h1,
        color: '#FFFFFF',
        fontSize: 48,
    },
    tagline: {
        ...theme.typography.body,
        color: '#FFFFFF',
        marginTop: theme.spacing.m,
    }
});

import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../navigation/types';
import { Button, Input, Header, ErrorMessage, Loading } from '../components';
import { theme } from '../theme/theme';
import { useAuth } from '../store/authStore';
import { ApiError } from '../services/apiClient';

type Props = {
    navigation: NativeStackNavigationProp<AuthStackParamList, 'Login'>;
};

export const Login = ({ navigation }: Props) => {
    const { signIn } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async () => {
        setError('');
        if (!email.trim() || !password) {
            setError('Please fill in both fields.');
            return;
        }

        setLoading(true);
        try {
            await signIn(email.trim(), password);
            // Navigation to HomeStack happens automatically via AppNavigator
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.detail);
            } else {
                setError('An unexpected error occurred. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Loading />;

    return (
        <SafeAreaView style={styles.container}>
            <Header title="Welcome Back" />
            <View style={styles.content}>
                {error ? <ErrorMessage message={error} /> : null}

                <Input
                    label="Email"
                    value={email}
                    onChangeText={setEmail}
                    autoCapitalize="none"
                    keyboardType="email-address"
                />
                <Input
                    label="Password"
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry
                />

                <Button title="Log In" onPress={handleLogin} loading={loading} />
                <Button
                    title="Create an account"
                    variant="outline"
                    onPress={() => navigation.navigate('Register')}
                />
            </View>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: theme.colors.background,
    },
    content: {
        flex: 1,
        padding: theme.spacing.m,
    },
});

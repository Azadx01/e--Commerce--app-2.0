import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../navigation/types';
import { Button, Input, Header, ErrorMessage, Loading } from '../components';
import { theme } from '../theme/theme';
import { useAuth } from '../store/authStore';
import { ApiError } from '../services/apiClient';

type Props = {
    navigation: NativeStackNavigationProp<AuthStackParamList, 'Register'>;
};

export const Register = ({ navigation }: Props) => {
    const { signUp } = useAuth();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleRegister = async () => {
        setError('');

        if (!name.trim() || !email.trim() || !password || !confirmPassword) {
            setError('All fields are required.');
            return;
        }
        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        if (password.length < 8) {
            setError('Password must be at least 8 characters.');
            return;
        }

        setLoading(true);
        try {
            await signUp(name.trim(), email.trim(), password);
            // AppNavigator automatically switches to HomeStack after signUp sets user
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.detail);
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Loading />;

    return (
        <SafeAreaView style={styles.container}>
            <Header title="Create Account" />
            <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
                {error ? <ErrorMessage message={error} /> : null}

                <Input
                    label="Full Name"
                    value={name}
                    onChangeText={setName}
                    placeholder="John Doe"
                />
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
                <Input
                    label="Confirm Password"
                    value={confirmPassword}
                    onChangeText={setConfirmPassword}
                    secureTextEntry
                />

                <View style={styles.spacer} />
                <Button title="Register" onPress={handleRegister} loading={loading} />
                <Button
                    title="Back to Login"
                    variant="outline"
                    onPress={() => navigation.goBack()}
                />
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    content: { padding: theme.spacing.m },
    spacer: { height: theme.spacing.m },
});

import React, { useCallback, useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useFocusEffect } from '@react-navigation/native';
import { HomeStackParamList } from '../navigation/types';
import { Header, Card, Button, EmptyState, Loading, ErrorMessage } from '../components';
import { theme } from '../theme/theme';
import { useAuth } from '../store/authStore';
import { deviceService, DeviceRead } from '../services/deviceService';
import { ApiError } from '../services/apiClient';

type Props = {
    navigation: NativeStackNavigationProp<HomeStackParamList, 'Home'>;
};

export const Home = ({ navigation }: Props) => {
    const { user } = useAuth();
    const [devices, setDevices] = useState<DeviceRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchDevices = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const data = await deviceService.list();
            setDevices(data);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.detail);
            } else {
                setError('Failed to load device summary.');
            }
        } finally {
            setLoading(false);
        }
    }, []);

    useFocusEffect(
        useCallback(() => {
            fetchDevices();
        }, [fetchDevices])
    );

    if (loading) return <Loading />;

    const activeDevices = devices.filter((d) => d.status === 'active');

    return (
        <SafeAreaView style={styles.container}>
            <Header title="ReVivo Dashboard" />
            <ScrollView contentContainerStyle={styles.content}>
                {/* Greeting */}
                <Text style={styles.greeting}>
                    Hello, {user?.name ?? user?.email ?? 'there'} 👋
                </Text>

                {error ? <ErrorMessage message={error} /> : null}

                {/* Summary card */}
                <Card style={styles.summaryCard}>
                    <Text style={styles.summaryLabel}>Registered Devices</Text>
                    <Text style={styles.summaryCount}>{devices.length}</Text>
                    <Text style={styles.summarySubLabel}>Active: {activeDevices.length}</Text>
                </Card>

                {devices.length === 0 ? (
                    <Card>
                        <EmptyState
                            title="No Active Devices"
                            description="Register your smartphone or laptop to start getting repair or resale estimates."
                        />
                    </Card>
                ) : (
                    <Card>
                        <Text style={styles.recentLabel}>Recent Devices</Text>
                        {devices.slice(0, 3).map((device) => (
                            <View key={device.id} style={styles.recentRow}>
                                <Text style={styles.recentName}>
                                    {device.brand} {device.model}
                                </Text>
                                <Text style={styles.recentMeta}>{device.category}</Text>
                            </View>
                        ))}
                    </Card>
                )}

                <Button
                    title="Manage My Devices"
                    onPress={() => navigation.navigate('Devices')}
                />
                <Button
                    title="My Profile"
                    variant="outline"
                    onPress={() => navigation.navigate('Profile')}
                />
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    content: { padding: theme.spacing.m },
    greeting: {
        ...theme.typography.h2,
        color: theme.colors.text,
        marginBottom: theme.spacing.m,
    },
    summaryCard: {
        marginBottom: theme.spacing.m,
        alignItems: 'center',
        paddingVertical: theme.spacing.xl,
    },
    summaryLabel: {
        ...theme.typography.caption,
        color: theme.colors.textSecondary,
        textTransform: 'uppercase',
        letterSpacing: 1,
    },
    summaryCount: {
        fontSize: 56,
        fontWeight: '700',
        color: theme.colors.primary,
        lineHeight: 64,
    },
    summarySubLabel: {
        ...theme.typography.body,
        color: theme.colors.textSecondary,
    },
    recentLabel: {
        ...theme.typography.caption,
        color: theme.colors.textSecondary,
        marginBottom: theme.spacing.s,
        textTransform: 'uppercase',
        letterSpacing: 1,
    },
    recentRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: theme.spacing.xs,
        borderBottomWidth: 1,
        borderBottomColor: theme.colors.border,
    },
    recentName: { ...theme.typography.body, color: theme.colors.text },
    recentMeta: { ...theme.typography.caption, color: theme.colors.textSecondary, alignSelf: 'center' },
});

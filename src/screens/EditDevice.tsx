import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';
import { HomeStackParamList } from '../navigation/types';
import { Header, Button, Input, ErrorMessage, Loading } from '../components';
import { theme } from '../theme/theme';
import { deviceService, DeviceUpdate } from '../services/deviceService';
import { ApiError } from '../services/apiClient';

type Props = {
    navigation: NativeStackNavigationProp<HomeStackParamList, 'EditDevice'>;
    route: RouteProp<HomeStackParamList, 'EditDevice'>;
};

export const EditDevice = ({ navigation, route }: Props) => {
    const { deviceId } = route.params;

    const [condition, setCondition] = useState('');
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');
    const [loadingData, setLoadingData] = useState(true);
    const [saving, setSaving] = useState(false);

    // Load existing device data
    useEffect(() => {
        const fetchDevice = async () => {
            setLoadingData(true);
            try {
                const device = await deviceService.get(deviceId);
                setCondition(device.condition ?? '');
                setStatus(device.status ?? 'active');
            } catch (err) {
                if (err instanceof ApiError) {
                    if (err.statusCode === 404) {
                        Alert.alert('Not Found', 'This device no longer exists.', [
                            { text: 'OK', onPress: () => navigation.goBack() },
                        ]);
                    } else if (err.statusCode === 403) {
                        Alert.alert('Forbidden', 'You cannot edit this device.', [
                            { text: 'OK', onPress: () => navigation.goBack() },
                        ]);
                    } else {
                        setError(err.detail);
                    }
                } else {
                    setError('Failed to load device.');
                }
            } finally {
                setLoadingData(false);
            }
        };

        fetchDevice();
    }, [deviceId]);

    const handleSave = async () => {
        setError('');

        setSaving(true);
        try {
            const payload: DeviceUpdate = {
                condition: condition.trim() || undefined,
                status: status.trim() || undefined,
            };
            await deviceService.update(deviceId, payload);
            Alert.alert('Success', 'Device updated successfully.', [
                { text: 'OK', onPress: () => navigation.goBack() },
            ]);
        } catch (err) {
            if (err instanceof ApiError) {
                if (err.statusCode === 403) {
                    setError('You do not have permission to edit this device.');
                } else if (err.statusCode === 404) {
                    setError('Device not found.');
                } else {
                    setError(err.detail);
                }
            } else {
                setError('Save failed. Please try again.');
            }
        } finally {
            setSaving(false);
        }
    };

    if (loadingData) return <Loading />;

    return (
        <SafeAreaView style={styles.container}>
            <Header title="Edit Device" />
            <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
                {error ? <ErrorMessage message={error} /> : null}

                <Input
                    label="Condition"
                    value={condition}
                    onChangeText={setCondition}
                    placeholder="e.g. Minor scratches"
                />
                <Input
                    label="Status"
                    value={status}
                    onChangeText={setStatus}
                    placeholder="active / pending / sold"
                />

                <View style={styles.spacer} />
                <Button title="Save Changes" onPress={handleSave} loading={saving} />
                <Button title="Cancel" variant="outline" onPress={() => navigation.goBack()} />
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    content: { padding: theme.spacing.m },
    spacer: { height: theme.spacing.m },
});

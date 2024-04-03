import { useState } from 'react';
import ServicesSubscriptionCard from './ServicesSubscriptionCard/ServicesSubscriptionCard';
import ServicesSubscriptionHistory from './ServicesSubscriptionHistory/ServicesSubscriptionHistory';
import ServicesSubscriptionInfo from './ServicesSubscriptionInfo/ServicesSubscriptionInfo';
import { ServiceSubscribeIcon } from '../../../../types/types';

export default function ServicesSubscription({ services }: { services: ServiceSubscribeIcon[] }) {
  const [infoVisible, setInfoVisible] = useState(true);

  const handleInfoClose = () => {
    setInfoVisible(false);
  };

  return (
    <>
      <ServicesSubscriptionCard services={services} />
      <ServicesSubscriptionHistory />
      {infoVisible && <ServicesSubscriptionInfo onClose={handleInfoClose} />}
    </>
  );
}
